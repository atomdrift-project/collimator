# Evaluation Methodology

This document defines how collimator partitions data, fits calibrators,
selects models, and reports metrics. It is the contract between the
training pipeline, autocollie's autonomous loop, and any paper or model
card the project publishes.

The single goal: every reported number is honest enough to defend in
print, with the simplest possible implementation that meets that bar.

## Three properties any reported number must hold

1. **No leakage.** Every row used to *select* a model, threshold, or
   feature is disjoint from every row used to *report* a metric.
2. **Statistical honesty.** Headline metrics ship with bootstrap CIs.
   "Winner beats baseline" claims ship with paired Δ-CIs and
   FDR-corrected p-values across the experiment family.
3. **Stated scope.** Limitations the data does not currently support
   (family-aware split, temporal split, strict-FP/100M precision floor)
   are named in the paper's Limitations section, not hidden.

## Partitions

Deterministic by `canonical_sha256` last byte:

| Range          | Partition | Approx size  | Use                                           |
|----------------|-----------|--------------|------------------------------------------------|
| `byte < 32`    | **test**  | 12.5%, ~286k | Final reported metrics. Touched once per submission. |
| `32 ≤ byte < 64` | **dev**   | 12.5%, ~286k | Selection, calibration, threshold search, autocollie screening. |
| `byte ≥ 64`    | **train** | 75%, ~1.7M   | Model fitting only. Never participates in selection or calibration. |

Properties:

- The `test` range is the same set of rows previously labeled "test."
  Historical run JSONs that report `test_metrics` retain their semantic
  meaning across the methodology change. They were leaky-test (used for
  selection); they are now honest-test only after the migration below.
- Every row's partition is computable from its canonical hash. No
  separate manifest, no per-snapshot drift.
- Archive-aware grouping (canonical SHA256 = lex-min over inner files)
  is preserved, so an archive and its constituents always co-locate.

What this partition does **not** prevent:

- **Family / campaign correlation** between train and dev/test (same
  actor, same packer, different content hashes). Documented in
  `experiments/NEXT_EXPERIMENTS.md` as deferred future work — the plan
  is to use `Sample.formula` as an informal cluster hash once test data
  regeneration produces usable formulas.
- **Concept drift** across time. The fs `mtime` field reflects when
  files were packed, not when they entered the corpus. Temporal split
  becomes feasible once hopper logs ingest timestamps and the corpus
  has enough time depth.

## Daily workflow

### Autocollie cycle

Per cycle, per route:

1. Train candidate config on `train` (75%).
2. Calibrate per-route isotonic on `dev` (12.5%).
3. Run threshold search on `dev` for L0..L100 operating points.
4. Report `dev_metrics` for the candidate.
5. Compare to route's historical baseline via paired bootstrap on `dev`
   rows. Promote to confirm-gate if the paired-Δ 95% CI excludes 0 and
   the mean Δ is operationally meaningful (≥ 0.001 F1 or as configured).

Compute is **the same as today, ~14% faster** because train is 75%
instead of 87.5%. No new training runs.

### Confirm gate

Triggered when screen flags a candidate. One additional train+calibrate
cycle on `train ∪ dev` (= 87.5%, same data volume as today's deployed
models), evaluated on locked `test` with bootstrap CIs.

This is the first time the candidate's config touches the test
partition, and the only time during a deployment cycle.

### Promotion

Confirm-gate passed → write
`experiments/autocollie/promote-<route>-<key>.md` with:

- 5-fold-equivalent dev metrics (mean ± bootstrap CI from `dev` rows).
- Paired Δ vs prior deployed config on `dev`, post-FDR p-value.
- Single locked-test number with bootstrap CI.
- The literal `make azoth-deploy` command.

Promotion does not deploy. The operator inspects all three numbers
before running deploy.

## Deployment

The deployed bundle is the model retrained on full `train ∪ dev`
(87.5%, ~2M rows), so the deployed instance has the same training
volume it has today. No data quality loss.

Calibration: reuse the dev-fit isotonic calibrator and threshold tuple
chosen during selection. Isotonic is monotone and rank-preserving;
adding 12.5% more training data shifts score magnitudes slightly but
preserves the rank order the calibrator was fit against. Acceptable for
v1.

If the deployed model's locked-test FP/100M deviates materially from
its dev FP/100M prediction (defined as outside the dev bootstrap CI),
refit the calibrator using an internal 80/20 split inside the 87.5%
retrain set as a one-time correction. Re-evaluate on test.

The locked-test evaluation is the headline number for the model card
and any paper claim. It is the only operation that touches the test
partition during a deployment cycle.

## Statistical reporting

Every metric in a model card, README table, or paper claim must carry
a CI. Every comparison claim must carry a paired test.

### Bootstrap CIs

Implemented in `src/collimator/stats.py` (to be added). Wraps
`scipy.stats.bootstrap`:

- `bootstrap_metric(y_true, y_score, metric_fn, B=1000, stratify=...)`:
  resample test rows with replacement, stratified by
  `(filetype, label)`; return point estimate + 2.5/97.5 percentile CI.
- `paired_bootstrap_diff(y_true, y_score_a, y_score_b, metric_fn, ...)`:
  same resamples for both models per iteration; return Δ-CI.

Used at:

- `experiment.py:_print_test_metrics`: every emitted metric gains a
  `ci_95: [lo, hi]` field in the run JSON.
- `azoth_calibrate_ensemble.py`: per-route metrics in the model card
  carry CIs.
- `MODEL.md`, `ENSEMBLE_MODEL.md`, `GENERALIST_MODEL.md`: tables show
  point + CI; current 4-decimal precision is replaced with whatever
  the CI half-width supports.

### Multiple-comparison correction

For experiment-family claims (`EXPERIMENTS.md` tables, autocollie
promotion logs), apply Benjamini-Hochberg FDR at q=0.05 across the set
of paired comparisons. Use
`statsmodels.stats.multitest.multipletests(method='fdr_bh')`. Claims
that don't survive correction are not "wins" and are not reported as
such.

### What gets dropped

- Point estimates without CIs.
- Deltas below the noise floor (~0.005 F1 with the current dev size)
  are not detectable; do not claim them.
- "100% precision" framing for routed FP-budget operating points; this
  is a class-balance artifact, not a model-quality result. Replace with
  (recall, FP/100M, absolute TP, absolute FP).
- Per-filetype tables for routes with < 200 test rows or < 30 minority
  class. Pool into a "tail" bucket; full per-route data goes to an
  appendix only if it's defensible.

## Optional: paper-quality 5-fold validation

If a venue requires k-fold cross-validation as a baseline, or a
specific claim needs power that single-split dev doesn't provide:

- Add a make target `azoth-paper-eval` that runs 5-fold CV on the
  general model + top 5 specialists, reporting mean ± std and
  paired-fold p-values.
- Run once before submission, parallel to other work. ~5× single-train
  compute, paid once.
- Output appended to the paper as supplementary methodology.

This is not part of the daily or deploy workflow. It exists as a
backstop for reviewer demands and high-stakes claims only.

## What's gained vs k-fold-everywhere

Trade-offs of single-split dev with bootstrap CIs vs full k-fold:

- **Lost**: ability to detect very small effects (Δ < ~0.005 F1)
  reliably. Mitigation: don't claim them. They're below clinical
  significance for malware detection anyway.
- **Lost**: tighter threshold-variance estimates at strict FP/100M.
  Mitigation: bootstrap the threshold search and report the resulting
  FP/100M CIs honestly. Strict-FP/100M precision is volume-floored
  regardless of split structure.
- **Kept**: leakage protection (dev/test disjoint, calibration on dev
  only).
- **Kept**: honest bootstrap CIs on every reported number.
- **Kept**: paired comparisons for selection claims.
- **Kept**: deployed model trained on 87.5% (same data quality as
  today).
- **Kept**: autocollie speed (no compute multiplier).

The net is full credibility for the standard requirements with no
daily compute increase.

## Migration plan

Each step lands and verifies before the next. Nothing destructive
until step 6.

1. **Partition API in `data.py`.** Add `is_dev_sample` and
   `partition_of`. Existing `is_test_sample` keeps its meaning.
   `stream_samples` gains `exclude_eval=True` (excludes both dev and
   test) and `only_dev=True`. Tests assert disjointness and ~12.5/12.5/75
   proportions.
2. **Per-fold caching infrastructure.** `thresholds/_inspect.py` cache
   key gains a `partition` field. Calibration scripts gain a
   `--partition=dev|test` argument. Existing full-corpus path remains
   for the leaky baseline comparison in step 5.
3. **Calibration moves to dev.** `azoth_calibrate_ensemble.py` and
   `thresholds/_inspect.py` filter to `partition=dev` for isotonic
   fitting and threshold search; `partition=test` for reporting.
4. **Bootstrap helpers.** New `src/collimator/stats.py` with
   `bootstrap_metric` and `paired_bootstrap_diff`. Wire into
   `_print_test_metrics`.
5. **Sanity-check comparison.** Run all three pipelines on the
   currently-deployed model: (a) leaky-train + leaky-cal (status quo),
   (b) leaky-train + per-partition cal, (c) full per-partition pipeline.
   Three numbers, one table. The gap between (a) and (c) is the
   methodology-gap finding for the paper.
6. **Honest retrain.** `make azoth-full-train` migrates to
   `exclude_eval=True`, calibrates on dev, evaluates on locked test.
   First fully honest end-to-end build.
7. **Autocollie integration.** Update `skill.md` and gate logic to use
   dev-bootstrap paired tests instead of fixed-threshold comparisons.
8. **Docs and cards.** Regenerate model cards with point + CI,
   replace "100% precision" framing, update README tables.

Estimated active engineering: ~3 days. Plus one fresh full-train +
recalibration cycle for the sanity-check baseline.

## Compute summary

| Operation                  | Today           | After             | Δ              |
|----------------------------|-----------------|-------------------|----------------|
| Autocollie screen cycle    | 1× train on 87.5% | 1× train on 75%   | ~14% faster    |
| Confirm gate               | 1× train on 87.5% | 1× train on 87.5% | unchanged      |
| Promote / deploy           | 1× train         | 1× train + bootstrap | +seconds       |
| Calibration                | full-corpus fit  | dev fit           | unchanged      |
| Headline reporting         | point estimate   | point + CI        | +seconds       |
| Paper-quality validation   | n/a              | 5× train (top routes) | one-time       |

No daily compute multiplier.

## Methodology-gap baseline (sanity check, 2026-05-09)

`scripts/azoth_methodology_gap.py` was run against the just-finished
`make azoth-full-train` bundle's threshold_scores cache. Same model,
three different evaluation views:

This historical study used a literal 0.5 FP/M target, then called L50.
Its saved measurements below are unchanged. Current level labels instead
follow [LEVELS.md](LEVELS.md); current L50 allows one calibration FP plus
an extrapolated 49 FP per 100 million benign files.

| View         | Rows      | F1     | ROC AUC | Brier  | recall at historical 0.5 FP/M |
|--------------|----------:|-------:|--------:|-------:|--------------:|
| full corpus  | 1,579,028 | 0.9760 | 0.9893  | 0.0086 | 0.7194        |
| train only   | 1,185,686 | 0.9766 | 0.9895  | 0.0084 | 0.7885        |
| dev only     |   196,758 | 0.9751 | 0.9891  | 0.0085 | 0.8935        |
| test only    |   196,584 | 0.9728 | 0.9878  | 0.0094 | 0.6933        |

Two findings worth highlighting:

1. **F1 leakage gap (full vs test) is modest** at threshold=0.5:
   +0.0032. The reported headline F1 of the current bundle is mildly
   inflated, not catastrophically. AUC and Brier move similarly.
2. **Strict-FP/100M precision floor is the bigger issue.** With ~157k
   benign rows in dev or test, that historical literal-rate budget was ~0 events
   (`floor(157k × 50 / 1e8) = 0`), so a single false positive moves the
   estimate by ~640 FP/100M (≈ 6.4 FP/M). This is a corpus-volume problem,
   not an allocation problem — k-fold CV on more benigns would help, but
   only at the cost of compute. That study accepted the floor and reported
   wide CIs. The current positive-level allowance includes an initial FP;
   it does not remove uncertainty in the extrapolated rate.

These numbers were computed by applying the dev/test partition
post-hoc to a model trained on byte ≥ 32 (which includes dev rows in
the training set). The first fully-honest end-to-end build (model
trained on byte ≥ 64 only, calibrated on dev only, evaluated on test
only) was pending at the time of that study. These historical numbers do
not establish the quality of a current train/dev/test-isolated bundle.

## Calibration design

### Headline metrics

- **PR AUC (`avg_precision`)** is the single ranking number we report
  and tune against. It captures the recall-vs-precision trade-off
  across the full operating range and is robust to the corpus's
  imbalance toward benigns — unlike ROC AUC, which is dominated by
  the easy benign mass on a 24:76 split.
- **Recall@L25** is the deployment-budget headline: detection under the
  shared one-FP-plus-increment allowance in [LEVELS.md](LEVELS.md), rather
  than a literal 25-FP/100M population-rate promise.
- **F-beta=2 threshold pick** at training time. The training step's
  per-route `optimal_threshold` is chosen on dev to maximize F2, biasing
  the deployed cut toward recall (β=2 ≈ recall weighted twice as much
  as precision). EMBER's heritage F1-optimum is a class-balanced summary
  not aligned with the security goal of catching malware at fixed
  benign cost; F2 is.
- **ROC AUC** stays in the table for academic continuity.

### Severity levels

The shared definition is [LEVELS.md](LEVELS.md), which supersedes earlier
literal-rate and interpolated-quantile descriptions here. L0 allows zero
observed calibration FPs. For positive L, a pool of N benign files has a
continuous allowance `1 + (L - 1) * N / 100_000_000`, rounded down for an
integer count budget. L1 allows one FP; L25 adds an estimated 24 FP/100M beyond
that initial FP. The deployed default is L25 on the L0..L25000 grid.

General, group, and type models share the final filetype decision allowance.
Dev selects the frozen policy; test measures it, including the runtime sweep
across levels. Measured counts, interpolated or extrapolated rate estimates,
and confidence bounds are separate. Neither a measured threshold nor an
extrapolated one guarantees that live traffic stays within the target.

### Per-filetype dimension

`azoth_route_policy_search.py` derives the same per-route interpolated quantile
thresholds within each filetype's row slice. For small filetypes
(e.g., ELF with ~14k benigns → empirical floor ~7000 FP/100M ≈ 70 FP/M
for resolvable qk) the strict-tier thresholds cluster at the 1-FP ceiling —
distinct but subtle per level via interpolation, never extrapolated above the
slice's benign scores; this is reported in `route_policies.md` per (filetype, level). Per-filetype policy
choice (general_only vs specialist_primary_with_escape, etc.) is then
made by `_choose_best` on the resulting OR-rule recall/F1, with an
inclusiveness tiebreaker that prefers specialist participation when
metrics tie (so litmus's `contains_route` check loads the specialist).

### Why not Clopper-Pearson budgets

An earlier design used Clopper-Pearson exact upper bounds at α=0.05 to
pick the largest dev FP count `x` whose 95% upper bound projected to ≤
qk FP/M, then optimized a coordinate-descent search over per-route
thresholds within that FP budget. We replaced it because:

1. The CP floor (~2000 FP/100M ≈ 20 FP/M for 150k dev benigns at
   α=0.05) collapsed strict L tiers into below-resolution markers
   without giving litmus meaningful severity discrimination at L0..L50.
2. The search-under-budget objective conflated *which threshold to
   deploy* with *what severity grade to assign*; severity grading
   doesn't need a confidence claim, only a description of the score's
   strictness.
3. Splitting the two — F2 picks the deploy threshold, quantile observation
   describes the severity grade — is cleaner than one objective trying
   to do both jobs.

CP bounds are still computed and reported (`cp_floor_per_100M` per
level) as honest annotations on how confidently any single observation
generalizes to deployment, but they no longer gate threshold selection.

### k=2 OOF for publication-grade calibration

For the rare publication run we use k=2 out-of-fold predictions on
train+dev (`make azoth-publish-train`). Effective benign sample becomes
~2.4M; the empirical floor drops from one-per-150k-benigns to
one-per-2.4M-benigns. Strict tiers become directly resolvable
empirically (no GPD extrapolation needed below ~40 FP/100M ≈ 0.4 FP/M).
Compute
cost: ~16h elapsed. Not the daily cadence, but the path when a paper
needs strict-tier numbers without extrapolation.

## Stated limitations

These belong in any paper's Limitations section, not hidden:

- **Family-aware split is deferred.** Train/test are content-deduplicated
  (canonical SHA256 prevents archive-level duplication) but not
  family-aware. Same actor, same packer, different content hashes can
  land on opposite sides of the split. Reported metrics may overstate
  generalization to truly unseen campaigns. Plan: implement
  formula-stratified splitting once test data regeneration produces
  usable formulas.
- **Temporal evaluation is deferred.** The fs `mtime` field reflects
  packing time, not corpus ingest time. Once hopper logs ingest
  timestamps and the corpus has enough time depth, time-blocked
  evaluation should be reported alongside random-split metrics.
- **Strict-tier severity thresholds.** Follow [LEVELS.md](LEVELS.md).
  Small pools can share count budgets across levels, and extrapolated rate
  estimates are uncertain. L0 means zero observed calibration FPs; it does
  not guarantee zero test or future FPs. Confidence bounds are reported
  separately from the operating-point allowance.
- **Inter-route FP correlation is not separately measured.** The
  routed FP budget is owned by the OR over routes; correlated FPs
  across routes inflate the budget conservatively (worst case) but
  fine-grained correlation analysis is left to future work.

## References

- `experiments/NEXT_EXPERIMENTS.md` — methodological roadmap, family-aware
  split plan.
- `azoth/DESIGN.md` — routed FP budget, score table, severity policy.
  The "Calibration Corpus" section reflects the dev/test partition
  semantics described here.
- EMBER 2018 (Anderson & Roth) — comparable single-held-out-test
  methodology. EMBER 2024 (Joyce et al., KDD'25) — temporal evaluation
  benchmark, used as reference baseline for the general-model
  comparison in `azoth/GENERALIST_MODEL.md`.
- TESSERACT (Pendlebury et al., USENIX 2019) — concept-drift critique
  of random splits in malware ML; cited in the Limitations section as
  motivation for deferred temporal evaluation.
