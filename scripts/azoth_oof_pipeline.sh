#!/usr/bin/env bash
#
# End-to-end honest-OOF publish pipeline — trains, OOF-scores, calibrates,
# gates and deploys the Azoth bundle. This is what `make azoth-publish-train`
# (and therefore `make nightly`) runs.
#
# ---------------------------------------------------------------- scheduling
#
# The work is six trainings plus three scoring/deploy stages. Run strictly
# back-to-back (what the old inlined publish-train recipe did) that measured
# ~11h on galadriel, 7h29m of which was the six trainings idling 126 of 128
# cores between LightGBM phases:
#
#   fold-A general 61m -> fold-A spec 52m -> fold-B general 56m ->
#   fold-B spec 54m -> prod general 138m -> prod spec 103m ->
#   oof-merge-general 43m -> oof-route-scores 84m -> deploy ~90m
#
# Instead we run TWO DEPENDENCY CHAINS concurrently. The chains are the natural
# fault lines: fold specialists need only their own fold's general, and the
# prod bundle needs only itself, so nothing in one chain waits on the other.
#
#   chain prod:  prod general (138m) ------------> prod specialists (103m)
#   chain fold:  fold-A gen (61m) -> fold-B gen (56m) -> fold-A spec (52m)
#                                                     -> fold-B spec (54m)
#
# Critical path becomes max(241m, 223m) = ~4h instead of 7h29m. The two chains
# are also deliberately BALANCED (241 vs 223) — that is why the folds are
# serialised against each other rather than fanned out three ways. A 3-way fan
# would not finish sooner (chain prod still gates at 241m) but would put three
# concurrent trainings on the box, and memory, not CPU, is the binding
# constraint here. **Never more than two heavy trainings are resident.**
#
# Then the two scoring stages, which are independent of each other (the general
# merge needs only the fold generals; the route merge needs the specialists),
# run as a pair: max(84m, 43m) = 84m instead of 127m. Total ~7h.
#
# The azoth-prefill-specialist-features stage is NOT part of this flow. It was
# meant to extract the train+dev union once and seed both folds' matrices, but
# its cache key is the sha256 of the general feature_spec.json it is pointed at
# (--general-dir, the PROD general by Makefile default), while a fresh fold
# specialist training looks up with its OWN fold general's spec — two different
# files, so the prefilled entries could never be hit. It was serial work on the
# critical path producing unusable entries. The make target still exists; making
# it actually pay would mean teaching it to write per-fold spec keys.
#
# ------------------------------------------------------------------- memory
#
# Concurrency here is bounded by RAM, not cores, and every OOM this pipeline
# has had came from processes that each measured the whole box and assumed it
# was theirs. Both admission clamps read /proc/meminfo MemAvailable at start:
#
#   * collimator's DB-fetch worker clamp (features.clamp_workers_to_available_ram)
#   * the specialist suite's parallelism clamp (azoth_specialist_suite.py)
#
# Two concurrent chains would each see the full free RAM and each admit a full
# budget — a 2x over-commit of the same bytes. So the parallel section exports
# COLLIMATOR_MEM_SHARES / AZOTH_CONCURRENT_SUITES = the number of concurrent
# consumers, and both clamps divide their headroom by it. The concurrent
# admissions then sum to what one sequential run would have taken, which is the
# operating point those per-fit estimates were calibrated against.
#
# MEM_LOG records MemAvailable every 60s for the whole run; the low-water mark
# is printed at the end. That is the number to look at before raising any
# parallelism knob — we have been tuning these blind.
#
# ------------------------------------------------------------------- stages
#
#   0. prod general      -> out/models/azoth/
#   1. fold-A general    -> out/models/azoth.oof-fold-a/
#   2. fold-B general    -> out/models/azoth.oof-fold-b/
#   3. azoth-oof-merge-general   43m  honest OOF general probs ->
#                                     out/models/azoth/general/threshold_scores.npz
#   4. fold-A specialists, and the prod specialists (the prod chain's
#      specialist step is gated here, not at stage 0, so STOP_STAGE=2 means
#      "generals only" in both chains)
#   5. fold-B specialists
#   6. azoth-oof-route-scores    84m  honest OOF specialist probs ->
#                                     out/models/azoth/oof_route_scores/
#   7. azoth-deploy              ~90m calibrate (--partition all, OOF route
#                                     scores) + diagnostics + policy search +
#                                     routed metrics + regression gate + litmus
#                                     validate + mirror into the deploy dir
#   8. azoth-shap                ~min per-route SHAP against the deployed
#                                     boosters (ascan --extra refuses stale)
#   9. headline numbers          reads the eval JSON stage 7 already wrote
#
# Stages 0-2 and 4-5 are scheduled by the chains above, not in numeric order;
# the numbers are resume points, not an execution order. START_STAGE/STOP_STAGE
# still gate each step individually.
#
# Usage:
#   scripts/azoth_oof_pipeline.sh
#   START_STAGE=4 scripts/azoth_oof_pipeline.sh   # resume after general OOF
#   START_STAGE=7 scripts/azoth_oof_pipeline.sh   # everything's trained,
#                                                 # just calibrate + deploy
#   STOP_STAGE=6 scripts/azoth_oof_pipeline.sh    # build OOF assets but
#                                                 # don't touch the deploy
#   PARALLEL_CHAINS=0 scripts/azoth_oof_pipeline.sh   # old sequential order
#
# If a stage fails the script exits; relaunch with START_STAGE=N to resume.

set -uo pipefail

cd "$(dirname "$0")/.."

START_STAGE=${START_STAGE:-0}
STOP_STAGE=${STOP_STAGE:-99}

OUT_ROOT=${OUT_ROOT:-out/models}
AZOTH_ROOT=${AZOTH_ROOT:-${OUT_ROOT}/azoth}
FOLD_A_ROOT=${OUT_ROOT}/azoth.oof-fold-a
FOLD_B_ROOT=${OUT_ROOT}/azoth.oof-fold-b
OOF_ROUTE_SCORES_DIR=${AZOTH_ROOT}/oof_route_scores

EVAL_OUT_MD=${AZOTH_ROOT}/route_policy_eval_oof.md
EVAL_OUT_JSON=${AZOTH_ROOT}/route_policy_eval_oof.json

NUM_STAGES=10  # stages 0..9

MEM_LOG=${MEM_LOG:-out/pipeline-mem.log}

stage_active() {
    local n=$1
    (( n >= START_STAGE && n <= STOP_STAGE ))
}

banner() {
    local n=$1 name=$2
    echo
    echo "================================================================"
    echo "[$n/$NUM_STAGES] $name"
    echo "================================================================"
}

skipped() {
    echo "[$1/$NUM_STAGES] SKIP (outside START_STAGE=$START_STAGE..STOP_STAGE=$STOP_STAGE): $2"
}

require_dir() {
    local label=$1 path=$2 stage=$3
    if [[ ! -d "$path" ]]; then
        echo "ERROR: ${label} missing at ${path}."
        echo "       Earlier stage ${stage} didn't complete. Resume with START_STAGE=${stage}."
        exit 2
    fi
}

require_file() {
    local label=$1 path=$2 stage=$3
    if [[ ! -f "$path" ]]; then
        echo "ERROR: ${label} missing at ${path}."
        echo "       Earlier stage ${stage} didn't complete. Resume with START_STAGE=${stage}."
        exit 2
    fi
}

mem_avail_gb() {
    awk '/^MemAvailable:/ { printf "%.0f", $2/1024/1024 }' /proc/meminfo 2>/dev/null
}

# Sample MemAvailable for the life of the run. We have repeatedly guessed at
# per-fit memory (28 GB/fit, 2 GB/worker) without ever recording what the box
# actually did, so every parallelism change has been a leap. This costs one awk
# per minute; the low-water mark it yields is the evidence for the next tuning
# decision. Killed via the EXIT trap.
MEM_WATCH_PID=""
start_mem_watch() {
    [[ -r /proc/meminfo ]] || return 0
    mkdir -p "$(dirname "$MEM_LOG")"
    echo "# $(date +%F' '%T) pipeline start (MemTotal $(awk '/^MemTotal:/ {printf "%.0f", $2/1024/1024}' /proc/meminfo) GB)" >> "$MEM_LOG"
    (
        while true; do
            echo "$(date +%F' '%T) mem_available_gb=$(mem_avail_gb) swap_free_gb=$(awk '/^SwapFree:/ {printf "%.0f", $2/1024/1024}' /proc/meminfo)"
            sleep 60
        done
    ) >> "$MEM_LOG" 2>/dev/null &
    MEM_WATCH_PID=$!
}
report_mem_watch() {
    [[ -n "$MEM_WATCH_PID" ]] || return 0
    kill "$MEM_WATCH_PID" 2>/dev/null
    wait "$MEM_WATCH_PID" 2>/dev/null
    MEM_WATCH_PID=""
    local low
    low=$(awk -F'mem_available_gb=' '/mem_available_gb=/ { split($2, a, " "); if (min == "" || a[1] < min) min = a[1] } END { print min }' "$MEM_LOG")
    [[ -n "$low" ]] && echo "[pipeline] MemAvailable low-water mark this run: ${low} GB (full trace: $MEM_LOG)"
}

# Chains run as background jobs; a failure in either must not leave the other
# orphaned to keep training for hours against a run that is already dead.
CHAIN_PIDS=()
cleanup() {
    local pid
    for pid in "${CHAIN_PIDS[@]:-}"; do
        [[ -n "$pid" ]] && kill "$pid" 2>/dev/null
    done
    [[ -n "$MEM_WATCH_PID" ]] && kill "$MEM_WATCH_PID" 2>/dev/null
    return 0
}
trap cleanup EXIT INT TERM

# Default the parallel chains on hosts with enough cores to absorb two
# concurrent trainings (>=32). Smaller boxes stay sequential: at 16 cores the
# per-LightGBM thread budget is already thin and halving it costs more than the
# overlap wins. GPU users should set PARALLEL_CHAINS=0 explicitly — device
# memory, not host RAM, is the binding constraint there and it is not shared out
# by the clamps below. PARALLEL_FOLDS is the pre-2026-08 name; still honoured.
if [[ -z "${PARALLEL_CHAINS:-}" ]]; then
    if [[ -n "${PARALLEL_FOLDS:-}" ]]; then
        PARALLEL_CHAINS=$PARALLEL_FOLDS
        echo "[pipeline] PARALLEL_CHAINS=$PARALLEL_CHAINS (from legacy PARALLEL_FOLDS)"
    elif (( $(nproc) >= 32 )); then
        PARALLEL_CHAINS=1
        echo "[pipeline] PARALLEL_CHAINS=1 (auto, $(nproc) cores)"
    else
        PARALLEL_CHAINS=0
        echo "[pipeline] PARALLEL_CHAINS=0 (auto, $(nproc) cores — below 32-core threshold)"
    fi
fi

NPROC=$(nproc)
CONCURRENCY=1
PAR_ARGS=()

# Training fidelity for the three generals. A publish run is full-corpus by
# definition — the whole point of k=2 OOF is the benign tail that sampling
# discards — so make azoth-publish-train hands the _FULL values down here and
# they are passed on each general's command line, out-ranking any
# DEPLOY_TRAIN_SAMPLES a caller left in the environment. Run standalone these
# are unset and the Makefile's own defaults (which already resolve to _FULL)
# apply.
FIDELITY_ARGS=()
[[ -n "${PUBLISH_TRAIN_SAMPLES:-}" ]] && FIDELITY_ARGS+=("DEPLOY_TRAIN_SAMPLES=$PUBLISH_TRAIN_SAMPLES")
[[ -n "${PUBLISH_MAX_TEST_SAMPLES:-}" ]] && FIDELITY_ARGS+=("DEPLOY_MAX_TEST_SAMPLES=$PUBLISH_MAX_TEST_SAMPLES")

# Split the box between the two chains for the whole parallel section.
#
#   COLLIMATOR_MEM_SHARES   halves the DB-fetch worker headroom (features.py)
#   AZOTH_CONCURRENT_SUITES halves the specialist parallelism headroom AND its
#                           per-fit thread/extract-worker budgets (the suite
#                           already read this for threads; it now also divides
#                           the memory admission, which is what was
#                           double-booked before)
#   COLLIMATOR_NUM_THREADS  caps each concurrent general's LightGBM at half the
#                           cores; without it TrainConfig asks for n_jobs=-1 =
#                           nproc per training and two of them put the box at
#                           2x oversubscription during the fit phase
#   WORKERS                 halves the REQUESTED DB-fetch parallelism, not just
#                           its ceiling. The clamps above only bind when the
#                           request exceeds them, so two chains asking for the
#                           nightly's WORKERS=24 would have run 48 concurrent
#                           postgres backends — more than the sequential run
#                           this is replacing, on a box whose OOM history is
#                           all fetch-worker memory. Halving keeps host-wide
#                           fetch concurrency identical to the proven-safe
#                           operating point; the wall-clock win comes from
#                           overlapping a fit-bound chain with an extract-bound
#                           one, not from more fetchers.
#
# Passed as make command-line assignments (not env) so they beat both the
# Makefile's `?=` defaults and anything inherited via MAKEFLAGS.
#
# Two, not three: the chain layout above never runs more than two heavy
# trainings at once, so a /3 split would leave a third of the RAM unused for
# the entire run.
if [[ "$PARALLEL_CHAINS" = "1" ]]; then
    CONCURRENCY=2
    export COLLIMATOR_MEM_SHARES=$CONCURRENCY
    export AZOTH_CONCURRENT_SUITES=$CONCURRENCY
    export COLLIMATOR_NUM_THREADS=$(( NPROC / CONCURRENCY ))
    CHAIN_WORKERS=$(( ${WORKERS:-$NPROC} / CONCURRENCY ))
    (( CHAIN_WORKERS < 1 )) && CHAIN_WORKERS=1
    PAR_ARGS=("WORKERS=$CHAIN_WORKERS")
    echo "[pipeline] 2 concurrent chains: COLLIMATOR_MEM_SHARES=2, AZOTH_CONCURRENT_SUITES=2," \
         "COLLIMATOR_NUM_THREADS=${COLLIMATOR_NUM_THREADS}, WORKERS=${CHAIN_WORKERS}/chain" \
         "(nproc=${NPROC}, requested WORKERS=${WORKERS:-$NPROC})"
    echo "[pipeline] MemAvailable at start: $(mem_avail_gb) GB"
fi

# Undo the split for stages that run alone — they should have the whole box.
unsplit_resources() {
    export COLLIMATOR_MEM_SHARES=1
    export AZOTH_CONCURRENT_SUITES=1
    unset COLLIMATOR_NUM_THREADS
    PAR_ARGS=()
}

start_mem_watch

# Resume is expressed by START_STAGE, NEVER by what happens to be on disk. An
# earlier version of this script skipped the prod general whenever a model file
# existed, to save time on repeat runs. That is wrong for a publish: the fold
# generals retrain unconditionally, so a stale prod general would be paired with
# folds trained on a newer corpus and the bundle shipped would be internally
# inconsistent — with nothing in the log saying so. If you want to keep a
# trained stage, skip it explicitly (START_STAGE=N).
#
# The one disk check that remains is a resume guard: stage 6 NEEDS the prod
# specialists summary (azoth_oof_score_routes.py reads the route -> file_type
# map from it and scores test rows with the prod models), so a resume that
# jumped past the training stages has to train them rather than die on a
# missing-file traceback after hours of stages 1-5.
prod_specialists_ready() {
    [[ -f "${AZOTH_ROOT}/specialists.json" ]]
}

# ------------------------------------------------------------------ chain prod
# prod general -> prod specialists. The long pole (241m), so it starts first and
# everything else is sized to finish inside it.
chain_prod() {
    if stage_active 0; then
        banner 0 "Train PROD GENERAL (no fold exclusion -> ${AZOTH_ROOT})"
        time make azoth-general AZOTH_GENERAL_SKIP_RESCORE=1 "${PAR_ARGS[@]}" "${FIDELITY_ARGS[@]}" || return 1
    else
        skipped 0 "prod general training"
    fi

    # The prod chain's specialist step is the third specialist training, so it is
    # gated with stages 4/5 rather than with stage 0 — STOP_STAGE=2 means "just
    # the generals" and must not train specialists in either chain.
    #
    # The second clause is a resume guard: stage 6 NEEDS the prod specialists
    # summary (azoth_oof_score_routes.py reads the route -> file_type map from it
    # and scores test rows with the prod models), so a resume that jumped past
    # the training stages trains them now rather than dying on a missing-file
    # traceback after hours of stages 1-5.
    #
    # SKIP_EXISTING=0 forces a real retrain: a publish must not ship specialists
    # left over from a previous run's general.
    if stage_active 4 || stage_active 5 || { stage_active 6 && ! prod_specialists_ready; }; then
        banner 4 "Train PROD SPECIALISTS (-> ${AZOTH_ROOT}/{filegroups,filetypes}/)"
        require_dir "prod general bundle" "${AZOTH_ROOT}/general" 0
        time make azoth-specialists AZOTH_SPECIALIST_SKIP_EXISTING=0 "${PAR_ARGS[@]}" || return 1
    else
        skipped 4 "prod specialist training"
    fi
    return 0
}

# ------------------------------------------------------------------ chain fold
# fold-A general -> fold-B general -> fold-A spec -> fold-B spec (223m). The two
# folds are serialised against each other on purpose; see the header.
chain_fold() {
    if stage_active 1; then
        banner 1 "Train fold-A GENERAL (EXP_OOF_FOLD_EXCLUDE=0 -> ${FOLD_A_ROOT})"
        time make azoth-general-fold-a "${PAR_ARGS[@]}" "${FIDELITY_ARGS[@]}" || return 1
    else
        skipped 1 "fold-A general training"
    fi

    if stage_active 2; then
        banner 2 "Train fold-B GENERAL (EXP_OOF_FOLD_EXCLUDE=1 -> ${FOLD_B_ROOT})"
        time make azoth-general-fold-b "${PAR_ARGS[@]}" "${FIDELITY_ARGS[@]}" || return 1
    else
        skipped 2 "fold-B general training"
    fi

    if stage_active 4; then
        banner 4 "Train fold-A specialists (-> ${FOLD_A_ROOT}/{filegroups,filetypes}/)"
        require_dir "fold-A general bundle" "${FOLD_A_ROOT}/general" 1
        time make azoth-specialists-fold-a "${PAR_ARGS[@]}" || return 1
    else
        skipped 4 "fold-A specialist training"
    fi

    if stage_active 5; then
        banner 5 "Train fold-B specialists (-> ${FOLD_B_ROOT}/{filegroups,filetypes}/)"
        require_dir "fold-B general bundle" "${FOLD_B_ROOT}/general" 2
        time make azoth-specialists-fold-b "${PAR_ARGS[@]}" || return 1
    else
        skipped 5 "fold-B specialist training"
    fi
    return 0
}

# ------------------------------------------------------------- run the chains
if stage_active 0 || stage_active 1 || stage_active 2 || stage_active 4 || stage_active 5; then
    if [[ "$PARALLEL_CHAINS" = "1" ]]; then
        echo
        echo "================================================================"
        echo "TRAINING: chain prod (general -> specialists) || chain fold"
        echo "          (fold-A gen -> fold-B gen -> fold-A spec -> fold-B spec)"
        echo "          2 concurrent trainings, RAM split 2 ways"
        echo "================================================================"
        chain_prod > >(sed 's/^/[prod] /') 2>&1 &
        PID_PROD=$!
        chain_fold > >(sed 's/^/[fold] /') 2>&1 &
        PID_FOLD=$!
        CHAIN_PIDS=("$PID_PROD" "$PID_FOLD")
        CHAIN_FAIL=0
        # Both chains are waited on even after one fails, deliberately. Every
        # training checkpoints to its own bundle dir, so letting the survivor
        # finish means the resume (START_STAGE=N) skips its stages outright
        # instead of repeating hours of work that had already succeeded.
        wait "$PID_PROD" || CHAIN_FAIL=1
        wait "$PID_FOLD" || CHAIN_FAIL=1
        CHAIN_PIDS=()
        if (( CHAIN_FAIL )); then
            echo "ERROR: a training chain failed (see the [prod] / [fold] lines above)."
            report_mem_watch
            exit 1
        fi
    else
        chain_prod || { report_mem_watch; exit 1; }
        chain_fold || { report_mem_watch; exit 1; }
    fi
    echo "[pipeline] trainings complete; MemAvailable now $(mem_avail_gb) GB"
fi

# ------------------------------------------------------------- scoring stages
# Stage 3 (general merge, 43m) and stage 6 (route merge, 84m) have no dependency
# on each other: 3 reads the two fold GENERALS, 6 reads the fold and prod
# SPECIALISTS. Both are extraction/DB-bound rather than fit-bound, so running
# the pair costs one 84m window instead of 127m sequential. Still only two
# concurrent consumers, so the same 2-way RAM split applies.
#
# PARALLEL_CHAINS=0 runs them back-to-back instead. That mode exists to be the
# low-memory fallback, and pairing them there would overlap two full-worker
# extractions with no split to pay for it — the opposite of what the setting
# asks for.
STAGE3_PID=""
STAGE3_LOG=""
if stage_active 3; then
    banner 3 "Merge OOF general predictions -> ${AZOTH_ROOT}/general/threshold_scores.npz"
    require_dir "fold-A general bundle" "${FOLD_A_ROOT}/general" 1
    require_dir "fold-B general bundle" "${FOLD_B_ROOT}/general" 2
    if [[ "$PARALLEL_CHAINS" = "1" ]]; then
        # Logged to a file rather than interleaved: two concurrent scoring
        # stages both emit per-batch progress and the mix is unreadable.
        STAGE3_LOG=$(mktemp -t azoth-oof-merge-general.XXXXXX.log)
        echo "[3] running concurrently with stage 6; streaming to ${STAGE3_LOG}, reaped before stage 7"
        (time make azoth-oof-merge-general "${PAR_ARGS[@]}") > "$STAGE3_LOG" 2>&1 &
        STAGE3_PID=$!
    else
        time make azoth-oof-merge-general "${PAR_ARGS[@]}" || { report_mem_watch; exit 1; }
    fi
else
    skipped 3 "OOF general merge"
fi

if stage_active 6; then
    banner 6 "Merge OOF route scores -> ${OOF_ROUTE_SCORES_DIR}"
    require_file "fold-A specialists summary" "${FOLD_A_ROOT}/specialists.json" 4
    require_file "fold-B specialists summary" "${FOLD_B_ROOT}/specialists.json" 5
    require_file "prod specialists summary" "${AZOTH_ROOT}/specialists.json" 0
    time make azoth-oof-route-scores "${PAR_ARGS[@]}" || { report_mem_watch; exit 1; }
else
    skipped 6 "OOF route-score merge"
fi

if [[ -n "$STAGE3_PID" ]]; then
    echo
    echo "Reaping backgrounded stage 3 (OOF general merge)..."
    if wait "$STAGE3_PID"; then
        echo "[3] OOF general merge succeeded; log tail:"
        tail -20 "$STAGE3_LOG"
    else
        echo "ERROR: backgrounded stage 3 (OOF general merge) failed; log:"
        cat "$STAGE3_LOG"
        rm -f "$STAGE3_LOG"
        report_mem_watch
        exit 1
    fi
    rm -f "$STAGE3_LOG"
fi

# ------------------------------------------------------------- deploy stages
# Everything below this point runs alone, so hand the whole box back: the split
# above would otherwise leave half the RAM and half the cores idle through the
# longest single stage in the run (calibrate re-extracts every route).
unsplit_resources

# azoth-deploy is the whole publish tail: calibrate (--partition all over the
# full OOF coverage, AZOTH_USE_OOF_ROUTE_SCORES=1 swapping each specialist's
# in-fold scores for its honest OOF scores) -> diagnostics -> route policy
# search -> global policy metrics -> routed metrics -> test-partition eval ->
# READMEs -> azoth-deploy-final (ONNX convert + validate + regression gate +
# litmus validate + mirror into the deploy dir). AZOTH_REFRESH_SCORES=1 forces
# a rescore so cached in-sample probs from a prior run cannot leak through: the
# OOF override fires inside _score_route, but the legacy calibration_scores.npz
# cache check happens FIRST.
if stage_active 7; then
    banner 7 "Calibrate + gate + deploy (azoth-deploy, honest OOF probs)"
    require_dir "OOF route scores" "${OOF_ROUTE_SCORES_DIR}" 6
    time make azoth-deploy \
        AZOTH_CALIBRATE_PARTITION=all \
        AZOTH_USE_OOF_ROUTE_SCORES=1 \
        AZOTH_REFRESH_SCORES=${AZOTH_REFRESH_SCORES:-1} || { report_mem_watch; exit 1; }
else
    skipped 7 "azoth-deploy"
fi

# Per-route SHAP against the freshly deployed boosters. Pure inference
# (~seconds/route) but not optional: ascan --extra refuses a bundle whose SHAP
# feature-space digest doesn't match its models, so skipping it ships a bundle
# with stale SHAP. Runs after stage 7 because the deploy's weakness prune
# decides which routes actually survive.
if stage_active 8; then
    banner 8 "Regenerate per-route SHAP (azoth-shap)"
    time make azoth-shap || { report_mem_watch; exit 1; }
else
    skipped 8 "azoth-shap"
fi

if stage_active 9 && [[ -f "$EVAL_OUT_JSON" ]]; then
    banner 9 "Headline numbers (from the eval stage 7 wrote)"
    .venv/bin/python -c "
import json, math
d = json.load(open('$EVAL_OUT_JSON'))
total_mal = caught = total_fp = 0
for ft, info in d['filetypes'].items():
    s = info.get('deployed_or_summary') or {}
    if not s: continue
    r = s.get('recall')
    if r is None or (isinstance(r, float) and math.isnan(r)): continue
    mal = info['malware']
    total_mal += mal
    caught += int(r * mal)
    total_fp += int(s.get('fp', 0))
if total_mal:
    print(f'  L9 hostile (default summary): {caught}/{total_mal} = {100*caught/total_mal:.2f}%  test_fp={total_fp}')
print(f'  Full eval report: $EVAL_OUT_MD')
"
fi

report_mem_watch
echo
echo "================================================================"
echo "Done."
echo "================================================================"
