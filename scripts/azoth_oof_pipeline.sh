#!/usr/bin/env bash
#
# End-to-end honest-OOF pipeline. Replaces the multi-day
# ``azoth-publish-train`` plus follow-on specialist OOF + recalibrate
# with a single resumable script.
#
# Stages (rough wall-clock estimates assume AZOTH_SPECIALIST_PARALLELISM=2):
#
#   0. azoth-general (prod)       ~1h    train prod general (no fold exclusion).
#                                        → out/models/azoth/
#                                        Needed by stage 6 (test-row scoring)
#                                        and stage 7 (calibrate). Skipped when
#                                        a fresh prod model already exists.
#   1. azoth-general-fold-a       ~1h    train general with fold 0 excluded
#                                        → out/models/azoth.oof-fold-a/
#   2. azoth-general-fold-b       ~1h    train general with fold 1 excluded
#                                        → out/models/azoth.oof-fold-b/
#   3. azoth-oof-merge-general    ~few h merge fold predictions →
#                                        out/models/azoth/general/threshold_scores.npz
#                                        (honest OOF general probabilities)
#   4. azoth-specialists-fold-a   ~27h   train specialists with fold 0 excluded
#                                        → out/models/azoth.oof-fold-a/{filegroups,filetypes}/
#   5. azoth-specialists-fold-b   ~27h   same with fold 1 excluded
#   6. azoth-oof-route-scores     ~few h merge per-route fold predictions →
#                                        out/models/azoth/oof_route_scores/
#                                        (honest OOF specialist probabilities;
#                                         test rows scored with production bundle)
#   7. azoth-calibrate            ~2h    recalibrate with OOF probs (sets
#                                        AZOTH_USE_OOF_ROUTE_SCORES=1)
#   8. azoth_route_policy_search  min    re-fit the ensemble policy on
#                                        unbiased data; recall-monotone floor
#                                        and joint-OR run honest now.
#   9. azoth_route_policy_eval    min    test-partition headline numbers.
#
# Total: roughly the same as the previous multi-day publish-train, but with
# clean checkpoints between every stage and ~2 days saved by NOT retraining
# specialists three times (the bug the Makefile split removed).
#
# Usage:
#   scripts/azoth_oof_pipeline.sh
#   START_STAGE=4 scripts/azoth_oof_pipeline.sh   # resume after general OOF
#   START_STAGE=7 scripts/azoth_oof_pipeline.sh   # everything's trained,
#                                                 # just re-calibrate + eval
#   STOP_STAGE=6 scripts/azoth_oof_pipeline.sh    # build OOF assets but
#                                                 # don't touch calibration
#
# If a stage fails the script exits; relaunch with START_STAGE=N to resume.

set -euo pipefail

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

NUM_STAGES=10  # stages 0..9; stage 0 (prod general) often a no-op skip

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

# Default PARALLEL_FOLDS=1 on hosts with enough cores to absorb 2×
# concurrent fold trainings (≥32 cores). Smaller boxes default to
# sequential — at parallelism=4 they'd already have only ~2 threads per
# LightGBM, and halving that under parallel folds tanks per-job
# throughput. GPU users should set PARALLEL_FOLDS=0 explicitly: device
# memory is the binding constraint, not CPU.
if [[ -z "${PARALLEL_FOLDS:-}" ]]; then
    if (( $(nproc) >= 32 )); then
        PARALLEL_FOLDS=1
        echo "[pipeline] PARALLEL_FOLDS=1 (auto, $(nproc) cores)"
    else
        PARALLEL_FOLDS=0
        echo "[pipeline] PARALLEL_FOLDS=0 (auto, $(nproc) cores — below 32-core threshold)"
    fi
fi

# When running parallel folds, tell each suite about the other so the
# auto thread-cap inside azoth_specialist_suite halves correctly.
# Without this the two suites would each claim nproc/parallelism threads
# per LightGBM job, doubling load and erasing the win.
if [[ "$PARALLEL_FOLDS" = "1" ]]; then
    export AZOTH_CONCURRENT_SUITES=2
fi

# Per-LightGBM thread cap for the GENERAL trainings. Stage 0 runs up to
# three generals concurrently (prod + fold-A + fold-B); without a cap
# each LightGBM uses n_jobs=-1 = nproc, so total LightGBM threads is
# 3 × nproc and the box ends up at 3× oversubscription during the
# LightGBM training phase. TrainConfig.__post_init__ reads
# COLLIMATOR_NUM_THREADS when num_threads is unset, so exporting it here
# caps every concurrent general training.
NPROC=$(nproc)
if [[ "$PARALLEL_FOLDS" = "1" ]]; then
    # Up to three concurrent generals (prod possibly skipped when fresh,
    # but cap for the worst case — under-utilization during fold-only
    # phases is fine; we never want oversubscription during overlap).
    export COLLIMATOR_NUM_THREADS=$(( NPROC / 3 ))
    echo "[pipeline] COLLIMATOR_NUM_THREADS=${COLLIMATOR_NUM_THREADS} (nproc=${NPROC} / 3 concurrent generals)"
fi

# Stage 0: train the prod general if it isn't already on disk. Needed
# by stage 6 (which scores test rows with the production model) and
# stage 7 (calibrate, which reads the prod specialists summary). The
# prod build uses its OWN EXP_OUT_DIR (out/experiments/azoth) — fold
# trainings get their own fold-specific workspaces, so all three can
# run truly in parallel with no clobbering. Skipped if a fresh prod
# model is already on disk (lets repeat runs / resumes avoid the
# re-train).
prod_general_ready() {
    [[ -f "${AZOTH_ROOT}/general/model.txt" ]] \
        || ls "${AZOTH_ROOT}/general/models/"seed_*.txt >/dev/null 2>&1
}
PROD_TRAIN_NEEDED=0
if stage_active 0; then
    if prod_general_ready; then
        echo "[pipeline] prod general already present at ${AZOTH_ROOT}/general/ — skipping stage 0"
    else
        PROD_TRAIN_NEEDED=1
    fi
fi

# Stages 0, 1, 2 are independent — each touches a distinct bundle root
# and experiment workspace (out/models/azoth, out/models/azoth.oof-fold-a,
# out/models/azoth.oof-fold-b respectively) and the experiment cache
# key includes oof_fold_exclude so the corpus + matrix caches don't
# collide either. With PARALLEL_FOLDS=1 we run all three concurrently.
# GPU users should override PARALLEL_FOLDS=0 because device memory is
# the binding constraint, not CPU.
if stage_active 1 && stage_active 2 && [[ "$PARALLEL_FOLDS" = "1" ]]; then
    if (( PROD_TRAIN_NEEDED )); then
        banner 0 "Train PROD AND fold-A AND fold-B GENERAL in parallel (PARALLEL_FOLDS=1)"
    else
        banner 1 "Train fold-A AND fold-B GENERAL in parallel (PARALLEL_FOLDS=1)"
    fi
    PID_PROD=""
    if (( PROD_TRAIN_NEEDED )); then
        (time make azoth-general AZOTH_GENERAL_SKIP_RESCORE=1) > >(sed 's/^/[prod]   /') 2>&1 &
        PID_PROD=$!
    fi
    (time make azoth-general-fold-a) > >(sed 's/^/[fold-A] /') 2>&1 &
    PID_A=$!
    (time make azoth-general-fold-b) > >(sed 's/^/[fold-B] /') 2>&1 &
    PID_B=$!
    if [[ -n "$PID_PROD" ]]; then wait "$PID_PROD"; fi
    wait "$PID_A" && wait "$PID_B"
elif stage_active 1; then
    if (( PROD_TRAIN_NEEDED )); then
        banner 0 "Train PROD GENERAL (no fold exclusion → ${AZOTH_ROOT})"
        time make azoth-general AZOTH_GENERAL_SKIP_RESCORE=1
    fi
    banner 1 "Train fold-A GENERAL (EXP_OOF_FOLD_EXCLUDE=0 → ${FOLD_A_ROOT})"
    time make azoth-general-fold-a
else
    skipped 1 "fold-A general training"
fi

if stage_active 2 && [[ "$PARALLEL_FOLDS" != "1" ]]; then
    banner 2 "Train fold-B GENERAL (EXP_OOF_FOLD_EXCLUDE=1 → ${FOLD_B_ROOT})"
    time make azoth-general-fold-b
elif [[ "$PARALLEL_FOLDS" = "1" ]] && stage_active 1; then
    # Already trained in parallel above.
    :
elif stage_active 2; then
    banner 2 "Train fold-B GENERAL (EXP_OOF_FOLD_EXCLUDE=1 → ${FOLD_B_ROOT})"
    time make azoth-general-fold-b
else
    skipped 2 "fold-B general training"
fi

# Stage 3 (OOF general merge) only needs the fold general bundles. Stage 4
# (fold-A specialist training) only needs the fold-A general FEATURE SPEC,
# not its OOF probs. They can run concurrently — and they SHOULD, because
# stage 3 is DB/extract-bound (idle CPU) and stage 4 is CPU-bound (idle DB).
# Overlapping recovers ~1-3 hours from the OOF pipeline. We background
# stage 3 here and reap it before stage 6 (the route-score merge), which
# is the first stage that actually depends on stage 3's output via the
# downstream calibrate consumer.
STAGE3_PID=""
STAGE3_LOG=""
if stage_active 3; then
    banner 3 "Merge OOF general predictions → ${AZOTH_ROOT}/general/threshold_scores.npz  (concurrent with stages 4-5)"
    require_dir "fold-A general bundle" "${FOLD_A_ROOT}/general" 1
    require_dir "fold-B general bundle" "${FOLD_B_ROOT}/general" 2
    # Send stage 3 output to a log file (interleaving with stages 4-5
    # would be hard to read at this level of concurrency).
    STAGE3_LOG=$(mktemp -t azoth-oof-merge-general.XXXXXX.log)
    echo "[3] streaming to ${STAGE3_LOG}; will reap before stage 6"
    (time make azoth-oof-merge-general) > "$STAGE3_LOG" 2>&1 &
    STAGE3_PID=$!
else
    skipped 3 "OOF general merge"
fi

if stage_active 4; then
    # Pre-build the cross-fold feature cache so stages 4-5 don't each pay
    # the per-fold extract. Runs ahead of (and serializes) the specialist
    # trainings — wall-clock saved exceeds this stage's cost because it
    # extracts the train+dev union ONCE instead of twice (and twice
    # concurrently, when PARALLEL_FOLDS=1, fighting for DB/workers).
    # Skipping when disabled via SKIP_PREFILL=1 (e.g. running only
    # stage 4-5 against an already-populated cache).
    if [[ "${SKIP_PREFILL:-0}" != "1" ]]; then
        banner_substage="[stage-4-prefill]"
        echo
        echo "================================================================"
        echo "$banner_substage Pre-fill route feature cache (shared across fold-A/-B)"
        echo "================================================================"
        time make azoth-prefill-specialist-features
    else
        echo "[stage-4-prefill] SKIP (SKIP_PREFILL=1)"
    fi
fi

if stage_active 4 && stage_active 5 && [[ "$PARALLEL_FOLDS" = "1" ]]; then
    banner 4 "Train fold-A AND fold-B specialists in parallel (PARALLEL_FOLDS=1)"
    require_dir "fold-A general bundle" "${FOLD_A_ROOT}/general" 1
    require_dir "fold-B general bundle" "${FOLD_B_ROOT}/general" 2
    # The specialist suite already parallelizes ACROSS routes via
    # AZOTH_SPECIALIST_PARALLELISM; running two fold trainings concurrently
    # adds a SECOND axis of parallelism. Halve AZOTH_SPECIALIST_PARALLELISM
    # via env when PARALLEL_FOLDS=1 if you're CPU/GPU constrained, e.g.:
    #   AZOTH_SPECIALIST_PARALLELISM=1 PARALLEL_FOLDS=1 scripts/azoth_oof_pipeline.sh
    (time make azoth-specialists-fold-a) > >(sed 's/^/[fold-A spec] /') 2>&1 &
    PID_A=$!
    (time make azoth-specialists-fold-b) > >(sed 's/^/[fold-B spec] /') 2>&1 &
    PID_B=$!
    SPEC_FAIL=0
    wait "$PID_A" || SPEC_FAIL=1
    wait "$PID_B" || SPEC_FAIL=1
    if [[ $SPEC_FAIL -ne 0 ]]; then
        echo "ERROR: at least one fold specialist training failed (see [fold-A spec] / [fold-B spec] lines above)"
        # Don't leave stage 3 hanging if we're about to bail.
        [[ -n "$STAGE3_PID" ]] && kill "$STAGE3_PID" 2>/dev/null
        exit 1
    fi
elif stage_active 4; then
    banner 4 "Train fold-A specialists (EXP_OOF_FOLD_EXCLUDE=0 → ${FOLD_A_ROOT}/{filegroups,filetypes}/)"
    require_dir "fold-A general bundle" "${FOLD_A_ROOT}/general" 1
    time make azoth-specialists-fold-a
else
    skipped 4 "fold-A specialist training"
fi

if stage_active 5 && [[ "$PARALLEL_FOLDS" = "1" ]] && stage_active 4; then
    # Already trained in parallel above.
    :
elif stage_active 5; then
    banner 5 "Train fold-B specialists (EXP_OOF_FOLD_EXCLUDE=1 → ${FOLD_B_ROOT}/{filegroups,filetypes}/)"
    require_dir "fold-B general bundle" "${FOLD_B_ROOT}/general" 2
    time make azoth-specialists-fold-b
else
    skipped 5 "fold-B specialist training"
fi

# Stage 3 was kicked off in the background after stages 1-2. Stage 6
# depends on its output (general/threshold_scores.npz feeds calibration
# downstream, but stage 6's OOF route merge doesn't strictly need it).
# Reap stage 3 here so a failure in the merge surfaces before stage 7.
if [[ -n "$STAGE3_PID" ]]; then
    echo
    echo "Reaping backgrounded stage 3 (OOF general merge) before stage 6..."
    if wait "$STAGE3_PID"; then
        echo "[3] OOF general merge succeeded; log:"
    else
        echo "ERROR: backgrounded stage 3 (OOF general merge) failed; log:"
        cat "$STAGE3_LOG"
        rm -f "$STAGE3_LOG"
        exit 1
    fi
    # Show the tail in success path so timing/progress is visible.
    tail -20 "$STAGE3_LOG"
    rm -f "$STAGE3_LOG"
fi

# Stage 6 also needs the PROD specialists summary at
# ${AZOTH_ROOT}/specialists.json — azoth_oof_score_routes.py loads the
# route → file_type mapping from it and scores test rows with the prod
# specialist models. Stage 0 trained the prod general but not the prod
# specialists; without this guard, the pipeline died right here on a
# missing-file traceback after spending hours on stages 1-5. Train it
# now if absent. Trains serially (no resource contention with stage 4-5
# which has already finished by this point).
prod_specialists_ready() {
    [[ -f "${AZOTH_ROOT}/specialists.json" ]]
}
if stage_active 6 && ! prod_specialists_ready; then
    banner 5b "Train PROD specialists (needed for stage 6 test-row scoring)"
    require_dir "prod general bundle" "${AZOTH_ROOT}/general" 0
    time make azoth-specialists
fi

if stage_active 6; then
    banner 6 "Merge OOF route scores → ${OOF_ROUTE_SCORES_DIR}"
    require_file "fold-A specialists summary" "${FOLD_A_ROOT}/specialists.json" 4
    require_file "fold-B specialists summary" "${FOLD_B_ROOT}/specialists.json" 5
    require_file "prod specialists summary" "${AZOTH_ROOT}/specialists.json" "5b (auto)"
    time make azoth-oof-route-scores
else
    skipped 6 "OOF route-score merge"
fi

if stage_active 7; then
    banner 7 "Re-calibrate with honest OOF probs (AZOTH_USE_OOF_ROUTE_SCORES=1)"
    require_dir "OOF route scores" "${OOF_ROUTE_SCORES_DIR}" 6
    # Force a rescore so cached in-sample probs from the prior run don't
    # leak through. The OOF override fires inside _score_route, but the
    # legacy calibration_scores.npz cache check happens FIRST — refreshing
    # bypasses it so we KNOW the score table carries honest probs.
    time make azoth-calibrate \
        AZOTH_USE_OOF_ROUTE_SCORES=1 \
        AZOTH_REFRESH_SCORES=${AZOTH_REFRESH_SCORES:-1}
else
    skipped 7 "azoth-calibrate"
fi

if stage_active 8; then
    banner 8 "Re-run route policy search on honest score table"
    require_file "score table" "${AZOTH_ROOT}/score_table.npz" 7
    time .venv/bin/python scripts/azoth_route_policy_search.py
else
    skipped 8 "route policy search"
fi

if stage_active 9; then
    banner 9 "Re-run test-partition eval → ${EVAL_OUT_MD}"
    require_file "route policies" "${AZOTH_ROOT}/route_policies.json" 8
    time .venv/bin/python scripts/azoth_route_policy_eval.py \
        --score-table "${AZOTH_ROOT}/score_table.npz" \
        --general-scores "${AZOTH_ROOT}/general/threshold_scores.npz" \
        --route-policies "${AZOTH_ROOT}/route_policies.json" \
        --partition test \
        --output-md "$EVAL_OUT_MD" \
        --output-json "$EVAL_OUT_JSON"

    if [[ -f "$EVAL_OUT_JSON" ]]; then
        echo
        echo "Headline numbers:"
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
else
    skipped 9 "policy eval"
fi

echo
echo "================================================================"
echo "Done. Bring the L0/L3/L9 test recall numbers back for PR 3."
echo "================================================================"
