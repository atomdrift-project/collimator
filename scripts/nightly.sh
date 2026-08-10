#!/usr/bin/env bash
#
# nightly.sh — unattended Azoth pipeline, split into two preemptible jobs.
#
#   nightly.sh train       repin -> azoth-publish-train (trains, regression-gates,
#                          and on success OOF-deploys the bundle into ../azoth via
#                          the $XDG_DATA_HOME/atomdrift/scan/models/azoth symlink)
#                          -> commit & push the azoth bundle (only if the deploy
#                          actually happened) -> hand the box back to the sweep.
#
#   nightly.sh autocollie  indefinite shuffled autocollie walk over every known
#                          route (general + all filegroups + all filetypes),
#                          until the next train preempts it.
#
# Why two jobs instead of one script that does both in sequence: a full
# publish-train runs 8-34h (the 2026-07-21 run took ~34h end to end), so a
# single daily unit routinely overran its own next firing and the flock made
# whole nights no-op. Splitting lets the sweep use every hour the train isn't.
#
# The two must never run concurrently — a full-corpus train peaks near 38G and
# an autocollie experiment alongside it is what drove the 2026-07-06/07/08
# OOMs. They don't lock against each other (a lock would just make the sweep
# skip whole days again); instead `train` *stops the sweep unit* before it
# starts any work, and *starts it again* when it's done. The sweep is therefore
# a best-effort idle-time filler: it gets every hour the train doesn't want and
# loses whichever experiment is in flight when the next train fires. systemd
# tears down the whole cgroup, so autocollie's python children die with it —
# the binary installs no SIGTERM handler of its own and doesn't need one.
#
# Run under systemd:
#   systemctl --user start azoth-nightly     (train; scheduled by make install-nightly)
#   systemctl --user start azoth-autocollie  (sweep; normally started by the train)
# or by hand via `make nightly` / `make nightly-sweep`.
#
# Output is written, line-timestamped, to out/nightly/<start-time>-<mode>.log
# (latest.log / latest-sweep.log symlinks; view with `make nightly-logs` /
# `make nightly-sweep-logs`) and also reaches journald via the service's stdout.
#
# Env overrides: NIGHTLY_EXPERIMENTS (default 1), NIGHTLY_PASSES (default 0 =
# loop until preempted), NIGHTLY_ALLOW_REGRESSION=1 (bypass the deploy
# regression gate), NIGHTLY_WORKERS (default 24; caps the retrain's DB-fetch
# parallelism — see the WORKERS export below).
set -uo pipefail

mode="${1:-train}"
case "$mode" in
  train|autocollie) ;;
  *) echo "usage: ${0##*/} [train|autocollie]" >&2; exit 2 ;;
esac

SWEEP_UNIT="azoth-autocollie.service"

export HOME="${HOME:-/home/t}"
# The deploy writes to $XDG_DATA_HOME/atomdrift/scan/models/azoth, a symlink to
# ../azoth. XDG_DATA_HOME is empty in a service/non-login shell, so pin it to the
# XDG default or the deploy resolves to /atomdrift/... and fails.
export XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
export PATH="/usr/local/bin:/usr/bin:/bin:$HOME/.local/bin:$PATH"
export LANG="${LANG:-C.UTF-8}"

cd "$(dirname "$(dirname "$(realpath "${BASH_SOURCE[0]}")")")" || exit 1   # collimator/
azoth="$(dirname "$PWD")/azoth"

# One run at a time *per mode*. Redundant with systemd for the scheduled run,
# but guards a manual `make nightly` colliding with an in-progress scheduled
# one. The two modes take different locks on purpose: the train holds its lock
# for its whole life and starts the sweep as its last act, so a shared lock
# would deadlock the hand-off. Train-vs-sweep exclusion is the stop/start
# below, not this flock. The train deliberately keeps the pre-split lock path
# so it still excludes a run started from an older copy of this script.
mkdir -p out
case "$mode" in
  train)      lock=out/nightly.lock ;;
  autocollie) lock=out/nightly-autocollie.lock ;;
esac
exec 9>"$lock"
flock -n 9 || { echo "another '$mode' run is active ($lock) — exiting."; exit 0; }

# Keep our own timestamped log. journald is not durable enough for a multi-hour
# run on this box: the journal is capped at SystemMaxUse=4G and the
# hopper/atomscan cluster churns through that in hours, so the run's entries
# get vacuumed before morning (and an unclean shutdown loses the tail — both
# bit us on 2026-07-16, leaving no record of an 11h run). The per-line
# timestamps are what make phase-timing post-mortems possible.
mkdir -p out/nightly
nightly_log="out/nightly/$(date +%F-%H%M%S)-$mode.log"
case "$mode" in
  train)      ln -sfn "$(basename "$nightly_log")" out/nightly/latest.log ;;
  autocollie) ln -sfn "$(basename "$nightly_log")" out/nightly/latest-sweep.log ;;
esac
find out/nightly -name '*.log' -type f -mtime +60 -delete
exec > >(gawk '{ print strftime("%F %T"), $0; fflush() }' | tee -a "$nightly_log") 2>&1
echo "nightly($mode): logging to $nightly_log"

[ -n "${NIGHTLY_ALLOW_REGRESSION:-}" ] && export AZOTH_ALLOW_REGRESSION=1

# Cap parallelism for the unattended run. The retrain's vocabulary pass
# (collimator experiment --workers, driven by EXP_WORKERS which defaults from
# WORKERS) is the memory hot spot, but not because the python side is large:
# the killed worker on the 2026-07-08 run held only ~11G RSS. Each of the N
# fetch workers opens its own postgres backend, so worker count is really a
# multiplier on *concurrent DB memory* — 32 workers on the full-corpus final
# train (~1.67M rows, ~2x a fold slice) drove a global OOM (CONSTRAINT_NONE,
# not a cgroup cap) while galadriel was also running atomscan (~35G) and the
# hopper cluster. The 2026-07-06 run OOM'd at full core count (~7min in); the
# 2026-07-07 run at 32 cleared both OOF folds but died on the final full train.
# 24 is a middle ground (2026-07-17, 16 made the run too slow): still under the
# 32 that OOM'd, and the mem-aware worker clamp (COLLIMATOR_MEM_AWARE_WORKERS,
# on by default) sheds workers under memory pressure — drop back to 16 if a
# full train OOMs again. WORKERS is the knob to set (not EXP_WORKERS):
# azoth-general re-forwards `--set EXP_WORKERS=$(WORKERS)` into the inner
# sub-make, so an EXP_WORKERS cap alone would be overridden. Override with
# NIGHTLY_WORKERS; unset it (NIGHTLY_WORKERS=) to fall back to the Makefile
# default of nproc. Applies to the sweep too — `make autocollie` threads
# WORKERS into its per-experiment --make-args.
#
# This is a HOST-WIDE budget, not a per-training one. Since 2026-08-07 the
# train runs two chains concurrently (scripts/azoth_oof_pipeline.sh) and that
# script halves this number per chain, so the box still sees ~24 concurrent
# fetch workers in total — the same operating point the value was tuned at.
# Raising it therefore raises host-wide fetch memory; check the MemAvailable
# low-water mark the pipeline now prints (out/pipeline-mem.log) before doing so.
if [ -n "${NIGHTLY_WORKERS-24}" ]; then
  export WORKERS="${NIGHTLY_WORKERS-24}"
  echo "nightly($mode): capping WORKERS=$WORKERS (DB-fetch parallelism)"
fi

# Bound pass-1 vocabulary memory (the phase the full-train OOM'd in) by pruning
# singleton n-grams every N merged batches. Off by default in collimator so
# ad-hoc/autocollie runs stay bit-reproducible; the *train* opts in because the
# full-corpus vocab is where the dicts blow up. Near-lossless (all min_freqs
# >= 5). Deliberately NOT applied to the sweep: autocollie compares experiment
# results across runs, so its feature vocab has to stay bit-reproducible with
# ad-hoc runs (before the train/sweep split this export leaked into the sweep).
# Set NIGHTLY_VOCAB_PRUNE_EVERY explicitly to force it either way. The
# mem-aware worker clamp (COLLIMATOR_MEM_AWARE_WORKERS) is on by default in
# collimator — no export needed; tune its headroom via COLLIMATOR_MEM_RESERVE_GB.
if [ "$mode" = train ] || [ -n "${NIGHTLY_VOCAB_PRUNE_EVERY:-}" ]; then
  export COLLIMATOR_VOCAB_PRUNE_EVERY="${NIGHTLY_VOCAB_PRUNE_EVERY-200}"
  [ -n "$COLLIMATOR_VOCAB_PRUNE_EVERY" ] && \
    echo "nightly($mode): vocab singleton-prune every $COLLIMATOR_VOCAB_PRUNE_EVERY batches"
fi

rc=0

# ---------------------------------------------------------------- sweep mode
if [ "$mode" = autocollie ]; then
  passes="${NIGHTLY_PASSES:-0}"
  echo "== autocollie sweep (every route, ${NIGHTLY_EXPERIMENTS:-1} experiment(s) each," \
       "$([ "$passes" = 0 ] && echo 'looping until preempted' || echo "$passes pass(es)")) =="
  make autocollie SHUFFLE_ROUTES=1 PASSES="$passes" \
    EXPERIMENTS="${NIGHTLY_EXPERIMENTS:-1}" || rc=1
  exit "$rc"
fi

# ---------------------------------------------------------------- train mode
# Take the box back from the sweep before touching anything. `stop` is a
# no-op-and-exit-0 when the unit is already inactive; it only fails when the
# unit isn't installed or there's no user manager, which is survivable.
echo "== preempt sweep =="
if systemctl --user stop "$SWEEP_UNIT" 2>/dev/null; then
  echo "stopped $SWEEP_UNIT (whole cgroup, incl. any in-flight experiment)."
else
  echo "no $SWEEP_UNIT to stop (not installed, or no --user manager) — continuing."
fi

echo "== repin =="
make repin || rc=1

echo "== azoth-publish-train (trains + gated OOF-deploy into $azoth) =="
if make azoth-publish-train; then
  echo "== commit + push =="
  git -C "$azoth" add -A
  if git -C "$azoth" diff --cached --quiet; then
    echo "azoth bundle unchanged — nothing to push."
  else
    git -C "$azoth" commit -m "nightly: azoth model update $(date +%F)" \
      && git -C "$azoth" push origin HEAD || rc=1
  fi
else
  rc=1
  echo "azoth-publish-train did not deploy — retrain failed, or the regression"
  echo "gate blocked a net-negative build (expected; nothing shipped). Full detail"
  echo "is above, or: journalctl --user -u azoth-nightly.service -b"
fi

# Hand the box to the sweep regardless of how the train went — a failed train is
# no reason to leave the machine idle until tomorrow. --no-block so we don't
# wait on a unit that is meant to run for the next ~15h.
echo "== hand off to sweep =="
if systemctl --user start --no-block "$SWEEP_UNIT" 2>/dev/null; then
  echo "started $SWEEP_UNIT (runs until the next train preempts it)."
  echo "follow it with: make nightly-sweep-logs"
else
  rc=1
  echo "ERROR: could not start $SWEEP_UNIT — the box will sit idle."
  echo "Install it with: make install-nightly   (or run: make nightly-sweep)"
fi

exit "$rc"
