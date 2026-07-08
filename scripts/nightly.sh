#!/usr/bin/env bash
#
# nightly.sh — unattended nightly Azoth retrain + publish + experiment sweep.
#
#   repin  ->  azoth-publish-train (trains, regression-gates, and on success
#   OOF-deploys the bundle into ../azoth via the
#   $XDG_DATA_HOME/atomdrift/scan/models/azoth symlink)  ->  commit & push the
#   azoth bundle (only if the deploy actually happened)  ->  autocollie sweep
#   over every known route, 2 experiments each.
#
# Run under `systemctl --user start azoth-nightly` (scheduled by
# `make install-nightly`) or by hand via `make nightly`. All output is captured
# by journald — view it with `make nightly-logs`.
#
# Env overrides: NIGHTLY_EXPERIMENTS (default 2), NIGHTLY_ALLOW_REGRESSION=1
# (bypass the deploy regression gate), NIGHTLY_WORKERS (default 32; caps the
# retrain's DB-fetch parallelism — see the WORKERS export below).
set -uo pipefail

export HOME="${HOME:-/home/t}"
# The deploy writes to $XDG_DATA_HOME/atomdrift/scan/models/azoth, a symlink to
# ../azoth. XDG_DATA_HOME is empty in a service/non-login shell, so pin it to the
# XDG default or the deploy resolves to /atomdrift/... and fails.
export XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
export PATH="/usr/local/bin:/usr/bin:/bin:$HOME/.local/bin:$PATH"
export LANG="${LANG:-C.UTF-8}"

cd "$(dirname "$(dirname "$(realpath "${BASH_SOURCE[0]}")")")" || exit 1   # collimator/
azoth="$(dirname "$PWD")/azoth"

# One run at a time. Redundant with systemd for the scheduled run, but guards a
# manual `make nightly` colliding with an in-progress scheduled one.
mkdir -p out
exec 9>out/nightly.lock
flock -n 9 || { echo "another nightly run is active — exiting."; exit 0; }

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
# 16 halves the concurrent fetch fan-out (both python- and postgres-side) and
# still clears the folds comfortably; the extra wall-clock is free in the 23h
# window. WORKERS is the knob to set (not EXP_WORKERS): azoth-general
# re-forwards `--set EXP_WORKERS=$(WORKERS)` into the inner sub-make, so an
# EXP_WORKERS cap alone would be overridden. Override with NIGHTLY_WORKERS;
# unset it (NIGHTLY_WORKERS=) to fall back to the Makefile default of nproc.
if [ -n "${NIGHTLY_WORKERS-16}" ]; then
  export WORKERS="${NIGHTLY_WORKERS-16}"
  echo "nightly: capping WORKERS=$WORKERS (retrain DB-fetch parallelism)"
fi

# Bound pass-1 vocabulary memory (the phase the full-train OOM'd in) by pruning
# singleton n-grams every N merged batches. Off by default in collimator so
# ad-hoc/autocollie runs stay bit-reproducible; the nightly opts in because the
# full-corpus vocab is where the dicts blow up. Near-lossless (all min_freqs
# >= 5). Set NIGHTLY_VOCAB_PRUNE_EVERY= to disable. The mem-aware worker clamp
# (COLLIMATOR_MEM_AWARE_WORKERS) is on by default in collimator — no export
# needed; tune its headroom via COLLIMATOR_MEM_RESERVE_GB if desired.
export COLLIMATOR_VOCAB_PRUNE_EVERY="${NIGHTLY_VOCAB_PRUNE_EVERY-200}"
[ -n "$COLLIMATOR_VOCAB_PRUNE_EVERY" ] && \
  echo "nightly: vocab singleton-prune every $COLLIMATOR_VOCAB_PRUNE_EVERY batches"

rc=0
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

echo "== autocollie sweep (every route, ${NIGHTLY_EXPERIMENTS:-2} experiments each) =="
make autocollie SHUFFLE_ROUTES=1 EXPERIMENTS="${NIGHTLY_EXPERIMENTS:-2}" || rc=1

exit "$rc"
