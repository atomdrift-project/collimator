# FP-Curve Estimation: Five Experiments Toward Full-Dynamic-Range Level Curves

Status: IMPLEMENTED + RUN (2026-08-03). Owner: t. Prereq reading:
METHODOLOGY.md ("Severity levels & the operating-point estimator").
**Results, leaderboard and recommendation: `FP_CURVE_RESULTS.md`.**
Code: `scripts/fp_curve_{bench,report,synth,all_routes}.py` and
`scripts/fp_curve_estimators/`. Nothing here has touched a shipped bundle.

## Goal

Produce **smooth, strictly monotone, accurately predicted level→threshold
curves** — evaluable at *any* level, including between grid anchors (L0–1,
L21–22, L250–300) and **below each route's resolution floor** — so that:

- `../scan` consumes a full dynamic range of FP-target levels per route, even
  for routes whose benign pool cannot measure those levels directly;
- `../website` / `../gauntlet` graph the nightly curve (downstream of scan
  output) without cliffs or flat artifacts;
- small routes (gem: 2,537 benign) get a usable severity dial instead of
  every strict level collapsing onto the same 1-FP cut.

The estimator refreshes in a **weekly batch** (hours of compute acceptable,
cached between runs, like `azoth-publish-train`). Nightly graphing consumes
its output; it does not re-fit nightly.

### What this changes, stated plainly

The incumbent (`collimator.thresholds.quantile_severity_threshold`) holds an
invariant: *never place a threshold above the max observed benign score*.
Extrapolating strict levels on small routes **intentionally relaxes that
invariant** — that is the entire point. METHODOLOGY.md records why the last
attempt (GPD, deleted 2026-06-06) failed: bounded-support overshoot past 1.0,
shape degeneracy below ~500 tail points, and no validation loop. Each
experiment below must clear a validation bar the old attempt never had. Until
a winner clears it, nothing here touches the shipped bundle.

## Current state (why the goal isn't met today)

- Thresholds are Type-7 interpolated benign quantiles — exact where
  measurable, but on a 25k-benign route every level in L1–L39 lands within
  one FP gap: the "curve" is flat, then steps.
- `_LOW_VOLUME_BENIGN_CUTOFF = 25_000` switches small routes to an
  absolute-FP reinterpretation (L_k → ⌈k/5⌉ FP, capped at 5% of benigns).
  The switch is a **cliff**: PE's eval slice crosses 25,000 depending on
  `min_sample_score` (24,776 vs 25,376), moving reported L25 recall ~10 pts
  for reasons unrelated to the model.
- Between-grid queries (L21, L22 are not grid anchors) have no defined
  answer; consumers get nearest-anchor behavior.
- The three intervals named in the goal are **unmeasurable on both target
  routes**: honest-floor ≈ 488 FP/100M (PE, 204,903 OOF benign) and
  ≈ 566 (ruby, 176,713). L0–1, L21–22, L250–300 all sit below both.

## Phase 0 (required, before benchmarking): maximize the measured base

The estimator experiments only cover the *modeled* region; the cheapest
resolution is the kind you measure. Audit result (2026-08-03): production
calibration already consumes full-route OOF pools when present
(`azoth_calibrate_ensemble.py` OOF override) — the 73 specialist routes'
floors are already honest and maximized. Two levers remain:

1. **Land the general-model OOF pool** — near-zero marginal cost: the
   machinery already exists (`make azoth-oof-merge-general` →
   `scripts/azoth_oof_score.py`, individually rerunnable) and the weekly
   `azoth-publish-train` chain produces it automatically at
   `$(AZOTH_GENERAL_DIR)/threshold_scores.npz`. As of 2026-08-03 a
   publish-train is in flight (fold-A/fold-B generals trained 01:49 /
   06:13; production-general phase running) — Phase 0 is *verify the
   merged file lands and wire it in as the deepest teacher*, not a new
   training job. Payoff: (a) ~10M-benign single-model teacher (train+dev
   OOF; floor ≈ 9 FP/100M) — direct L21–22 verification instead of
   aggregate-only; (b) an honest curve for the general route itself.
   Historical candidate bundles (e.g.
   `out/models/azoth-tail-promote-l3/general/threshold_scores.npz`) prove
   the format; do not use them as teachers — they are candidate-config,
   sample-capped runs.
2. Benign corpus growth for starved routes (gem, rtf, lnk, applescript) —
   complementary, out of scope here, but note every 10× of real benigns
   removes a decade of extrapolation no estimator has to earn.

Related, model-side: the PE iteration work (2026-08-03, round 1) showed the
benign tail is *trainable* — fp=1 recall moved 66→81% on hyperparameters
alone. A model trained to spread its benign pileup near 1.0 shortens the
extrapolation for every estimator below. That thread stays coupled but
separate.

## Shared benchmark (all five experiments run against this)

### Data substrate

Honest scores only:

- `out/models/azoth/oof_route_scores/filetypes/<route>/threshold_scores.npz`
  — route-complete out-of-fold probabilities (`probs`, `labels`, `row_ids`).
  In-sample scores on train rows (as in `score_table.npz` train partitions)
  are optimistically biased and MUST NOT feed tail fits or oracles.
- Raw multi-seed-averaged probabilities, never isotonic-calibrated ones
  (piecewise-constant plateaus poison tail fits).
- All fitting in **logit space** (`log(p/(1−p))`): unbounded support, no
  overshoot past 1.0 by construction.

### Evaluation targets

| route | benign (OOF) | malware | floor FP/100M | role |
|---|---|---|---|---|
| pe   | 204,903 | 1,374,477 | ~488 | mid-size, the motivating case |
| ruby | 176,713 | 398       | ~566 | user-named; NOTE: malware side is tiny → recall-domain metrics are noise-limited there; score ruby on threshold-domain metrics |
| gem  | 2,537   | 899       | ~39,400 | sub-cliff tier; the "full dial for smaller models" stress case |

### Oracle: scale-ladder backtest

No target route can measure the named intervals, so accuracy is scored where
deep quantiles ARE measurable and estimators are asked to reach them from
less data:

**Teacher pools** — single-model honest OOF benign scores only (measured
2026-08-03 from `oof_route_scores/*/threshold_scores.npz`; re-verify counts
at run time):

| teacher | benign | floor FP/100M |
|---|---|---|
| filegroups/scripts | 2,970,762 | 33.7 |
| filegroups/source | 2,577,199 | 38.8 |
| filetypes/java_class | 1,702,485 | 58.7 |
| filegroups/portable | 1,707,830 | 58.6 |
| filetypes/c | 1,537,043 | 65.1 |
| filetypes/javascript | 1,364,820 | 73.3 |

There is **no general-model OOF pool today** — do NOT substitute
`score_table.npz`'s 12.3M "global" benigns: that table mixes in-sample
scores on train rows (optimistically biased) and per-route model score
distributions (not one distribution). Phase 0 builds the real thing
(general OOF, floor ≈ 8 FP/100M); once it exists, add it as the deepest
teacher and upgrade L21–22 from aggregate-only to direct verification.

**Protocol**: from each teacher pool, draw B (≥50) subsamples at rung sizes
m ∈ {800, 2,500, 25,000, 200,000} (≈ rtf / gem / PE-eval-slice / PE-full
scales). Each estimator fits on the subsample only (plus whatever pooled
context its method defines — pooling context must exclude the teacher route
to prevent leakage) and predicts thresholds at verification levels. Realized
FP is then counted on the **full teacher pool** at the predicted threshold.

**Verification depths**: strong verification (≥~5 expected FP on the full
pool) starts at ~L170 (scripts) / ~L195 (source) / ~L300 (java_class) —
L250–300 is well covered. Between ~L35 and ~L170 the biggest pools expect
0.5–5 FP per evaluation: individual draws are uninformative, but the
*aggregate* over B≥50 draws still detects calibration bias (Poisson scoring
— a 3× rate overshoot at L40 shows up unmistakably across 50 draws).
**L21–22** sits at ~0.6–0.7 expected FP on the scripts pool: aggregate-bias
detection only, unless the optional general-OOF build above is run.

**L0–1 blind spot and the synthetic-tail suite** (scoped in 2026-08-03,
superseding the earlier descope): no empirical oracle exists at L0–1 —
direct verification would need ~100M benigns under one model.
Rung-consistency (m=25k and m=200k fits of the same pool agreeing within
CI) catches *instability* but not *consistent bias*: an estimator wrong the
same way at every scale passes it. The synthetic suite closes that hole —
the only possible source of absolute error bars at L0–1:

- **Spliced-real tails**: empirical body from a big pool, analytic tail
  grafted beyond a splice point — truth known exactly, body realistic.
- **Adversarial shapes**, deliberately wider than any estimator's
  assumption class: mixture bumps near 1.0 (PE's dual-use-tool pileup),
  truncated tails, discrete atoms (single-seed GBDT scores), contaminated
  tails.
- **Anti-circularity rule**: report per-shape, never averaged — a method
  that only wins on its own assumption family (e.g. GPD estimators on
  GPD-simulated tails) is exposed, not rewarded.

With the suite, the L0–1 gate upgrades from consistency-only to
*synthetic-calibration-bounded*: a winner must show bounded error across
the full shape family before scan consumes that end of the dial.

### Metrics

1. **Tail calibration** (primary): Poisson deviance between predicted and
   realized FP counts at verification levels, aggregated per (pool, m) task;
   weight small-m rungs 2× (they are the deployment case).
2. **Threshold error**: |logit t̂ − logit t*| at levels the pool measures.
3. **Recall error**: |R(t̂) − R(t*)| using the route's malware scores
   (operational impact; skip for ruby per above).
4. **CI coverage**: fraction of verification points where realized FP falls
   inside the estimator's 90% band (target ≥ 85%).
5. **Smoothness / dynamic range**: strict monotonicity over continuous
   levels (hard gate); fraction of grid levels with distinct thresholds
   ("dial resolution"); total variation of d(logit t)/d(log level).
6. **Cliff test**: fit at n=24,776 vs n=25,376 draws of the same pool; curve
   distance must be ≈ sampling noise (kills the 25k regime discontinuity).
7. **Stability**: bootstrap sd of thresholds per level at each rung.

### Baseline B0

The incumbent estimator exactly as shipped (interpolated quantile + 25k
cliff + absolute-FP regime), run through the identical harness. Every
experiment reports deltas against B0. B0 is expected to win measured-region
fidelity by definition and lose dynamic range and the cliff test — the
question is who beats it below the floor without losing above it.

### Common estimator API

```python
fit(logit_benign: np.ndarray, route_meta: RouteMeta, context: PooledContext)
  -> CurveModel
CurveModel.threshold(level: float) -> float          # continuous, strictly monotone
CurveModel.band(level: float, q: float) -> (lo, hi)  # CI
CurveModel.to_grid(levels: Sequence[float]) -> table # bundle/scan emission
```

One harness runs all five plus B0; results land in a single leaderboard.

## The five experiments

### EXP-1 `smooth-interp` — smoothed order statistics, no extrapolation (control)

Harrell–Davis quantile estimation (beta-kernel weighted average of all order
statistics) on logit scores, then a shape-constrained monotone spline in
(log(1+level), logit t) space. Below the route floor: clamp at the floor
value, flag `model_extrapolated=false`.

- *Hypothesis*: smoothness alone fixes between-grid queries, graph quality,
  and the cliff — without extrapolation risk.
- *Why it wins*: zero new failure modes; best possible measured-region
  fidelity among smooth curves; trivially cheap.
- *Why it loses*: fails "full dynamic range" below the floor **by design**.
  It is the honesty control: any extrapolating method must beat it on tail
  calibration to justify existing.
- Effort: ~0.5 day.

### EXP-2 `logit-gpd` — per-route peaks-over-threshold, penalized

Classical EVT done with the three fixes the deleted version lacked:
exceedances over u = ~90–95% logit-benign quantile (u chosen per route by
automated parameter-stability scan), GPD fit by penalized MLE (Coles-style
penalty on shape ξ; PWM fallback on failure), Weissman-type quantile
extrapolation, profile-likelihood CIs. Empirical below u, GPD above,
continuity enforced at the seam.

- *Hypothesis*: with unbounded support and a regularized shape, POT is
  accurate 1–2 decades beyond the floor — which is exactly the gap
  (25k → 4M is ~2.2 decades; 200k → 4M is ~1.3).
- *Why it wins*: principled, decades of literature, seconds per route,
  interpretable ξ per route.
- *Why it loses*: gem-scale pools give ~130–250 exceedances — ξ variance may
  still be too high even penalized; per-route independence wastes the fact
  that route tails are related.
- Effort: 1–2 days.

### EXP-3 `pooled-tail` — hierarchical Bayesian GPD

Three-level hierarchy in logit space: global → filegroup → route on GPD
(ξ, σ), partial pooling, fit weekly by NUTS or SVI (numpyro); posterior
predictive quantiles and credible bands fall out directly. Small routes
inherit the family tail and deviate only where their data insists.

- *Hypothesis*: route tails within a filegroup share shape; borrowing
  strength is the statistically right way to give gem a dial it cannot
  estimate alone. Replaces the 25k cliff with continuous shrinkage.
- *Why it wins*: expected best-in-class on small routes; principled CIs;
  the hierarchy mirrors the existing route topology.
- *Why it loses*: pooling bias when a route's benign tail genuinely differs
  from its family (PE's dual-use-tool pileup near 1.0 may be exactly such a
  case — check shrinkage diagnostics); heaviest engineering lift.
- Effort: 3–4 days (fits comfortably in the weekly-batch budget).

### EXP-4 `boosted-tail` — covariate-conditional GPD (gbex-style)

Gradient-boosted conditional GPD: trees minimize GPD deviance with
covariates = route one-hots, filegroup, log n_benign, and benign score-body
moments (logit-mean/sd/skew, fixed-quantile anchors). Leave-route-out CV.
Direct descendant of gbex (Velthoen–Cai–Engelke–Zhou, *Extremes* 2023);
EQRN is the NN sibling.

- *Hypothesis*: learned covariate structure captures tail regularities the
  fixed hierarchy misses ("learned pooling").
- *Why it wins*: flexibility; automatic relevance of covariates; the
  literature shows it beating both plain QR and unconditional EVT.
- *Why it loses*: ~70 routes is a small effective sample of *tails*; risk of
  leaning on body moments that don't determine tail behavior.
- Effort: 2–3 days.

### EXP-5 `ladder-learned` — meta-estimator trained on the ladder itself

Supervised extrapolation: training pairs are (empirical curve of an m-sized
subsample + covariates) → (full-pool deep quantiles), constructed by the
thousands from the teacher pools. A monotone-constrained GBM/NN predicts
logit-threshold *offsets* Δ(level) added to EXP-1's smooth interpolation.
Leave-route-out: never trained on the pool it's evaluated on.

- *Hypothesis*: directly optimizing "small pool in → deep curve out" beats
  generative tail modeling, the same way discriminative usually beats
  generative when the target task is fixed.
- *Why it wins*: it is literally trained on the benchmark objective;
  distribution-free assumptions.
- *Why it loses*: only 4 teacher pools → transfer risk to unseen score
  distributions; must demonstrate leave-route-out generalization or it's
  memorizing LightGBM-tail idiosyncrasies.
- Effort: 2–3 days (after the harness exists).

### All-routes application pass

"Across all models" is demonstrated, not asserted: after the leaderboard,
the top-2 estimators are fit on **all 73 routes** and run through a
diagnostics battery — strict monotonicity, CP-bound consistency,
family-shape outlier detection (a route whose fitted tail deviates wildly
from its filegroup gets flagged for eyes-on review), and fit-failure count.
The deliverable is a per-route table; a winner that fails >5% of routes or
any high-volume route is not a winner regardless of its ladder score.
pe/ruby/gem remain the *deep-dive* targets; this pass is the breadth gate.

## Decision rule

Primary ranking: tail-calibration deviance (metric 1) across ladder tasks.
Hard gates for any winner:

1. Measured-region fidelity within CI of empirical quantiles (do no harm
   above the floor);
2. Strict monotonicity over continuous levels, full grid range;
3. Cliff test passes (25k discontinuity gone);
4. Distinct thresholds across the full dial (EXP-1 exempt, as control);
5. CI coverage ≥ 85% at nominal 90%.

If no extrapolating method beats EXP-1 on tail calibration while passing the
gates, **ship EXP-1** — smooth honest curves with a flagged floor — and
revisit after the corpus grows.

## Rollout & guardrails (winner only)

- Weekly batch job emits per-route level→threshold tables (denser grid than
  today's 42 anchors; scan contract unchanged — it reads a table).
- Every sub-floor row carries `model_extrapolated: true` plus the
  Clopper-Pearson bound (`cp_floor_per_100M`) so no consumer can mistake a
  model claim for a measurement.
- Fallback to B0 per route on fit failure or diagnostics out of range.
- **Production backtest forever**: gauntlet's nightly graphs add
  predicted-vs-realized FP tracking; a route whose realized FP exceeds its
  predicted band gets flagged and reverts to B0 at the next weekly batch.
- Deploy gates / promote logic keep using measured quantiles until a
  separate, later decision — out of scope here.

## Out of scope

- Synthetic-tail validation (descoped 2026-08-03; would be the only way to
  put absolute error bars on L0–1).
- Any change to autocollie promote gates or litmus deploy validation.
- Growing the benign corpus (separate, complementary lever: k=2 OOF pooling
  already documented in METHODOLOGY.md).

## Appendix: implementation bootstrap (for a fresh session)

Everything needed to start with zero conversation context.

### Environment

- Repo: `/home/t/collimator`. Python: `.venv/bin/python`. Import pattern:
  `sys.path.insert(0, "src")` then `from collimator import thresholds`.
- **No database access required** — the entire benchmark reads the npz
  files below. (`DB` is only needed if you regenerate OOF scores.)
- Do not run `git add/commit/push`; the operator handles all git state.
- Scratch/intermediate files: `out/experiments/fp_curves/` (create it).

### Data files and schema

`out/models/azoth/oof_route_scores/{filetypes,filegroups}/<route>/threshold_scores.npz`
(73 files). Keys:

| key | dtype | meaning |
|---|---|---|
| `probs` | float32 | **model probability — the score to use.** Clip to [1e-7, 1−1e-7] before logit. |
| `labels` | int8 | 1 = malware, 0 = benign |
| `scores` | int32 | hopper corpus score (sample metadata). **NOT a model output — do not fit tails on this.** |
| `row_ids`, `sha256`, `canonical_shas` | — | identifiers |
| `corpus_*` | int64 scalars | snapshot bookkeeping |

Multi-seed-averaged raw probabilities; never use isotonic-calibrated scores
(piecewise-constant plateaus) and never use `score_table.npz` for tail fits
(in-sample train rows).

### Incumbent (baseline B0) entry points

```python
from collimator.thresholds import quantile_severity_threshold
thr, method = quantile_severity_threshold(benign_probs,      # PROB space, not logit
                                          target_per_million=level / 100.0)
# method ∈ {"empirical", "absolute_fp", "none"(<50 benigns)}
```

- Level math: level k ⇔ k FP per 100M ⇔ p = k×1e-8; expected FP = n_benign·p.
- Regime cliff: `thresholds._LOW_VOLUME_BENIGN_CUTOFF == 25_000`; below it
  (and n·p < 1) levels become absolute FP counts via `_resolution_aware_fp`.
- Grid: `thresholds._LEVELS_PER_100M` (42-tuple, 0…25000).
- **TRAP**: `thresholds.SEVERITY_LEVEL_TARGETS` is a positional list; the
  real level is each dict's `["level"]` field. Never use the enumerate index
  as the level — `azoth_specialist_suite._level_table` did and emitted a
  100×-off table. Correct usage: `scripts/elf_model_benchmark.py:259`.

### Prior art in-repo

- `scripts/pe_iterate.py::fp_curve` — recall at absolute benign-FP counts
  (the regime-independent reporting convention this proposal adopts).
- `scripts/compute_routed_metrics.py::_recall_at_fpr_per_million` — the
  shared-estimator metric path.

### Suggested layout

- `scripts/fp_curve_bench.py` — harness: loads pools, draws rungs, runs
  estimators, writes one JSONL row per (estimator, pool, m, draw, level)
  to `out/experiments/fp_curves/`.
- `scripts/fp_curve_estimators/` — `b0.py`, `exp1_smooth_interp.py` …
  `exp5_ladder_learned.py`, each implementing §Common estimator API.
- Determinism: per-draw RNG seed = stable hash of (pool, m, draw_idx).
- Build order: harness + B0 + EXP-1 first (validates the harness end to
  end with zero extrapolation risk), then EXP-3 (single most likely
  winner: the hierarchy matches the route topology and small routes are
  the hard case) → EXP-2 (cheap classical reference) → EXP-4/EXP-5
  (second wave; EXP-5 needs the ladder data EXP-1–3 runs generate anyway).

### Leakage and scale rules

- When a teacher pool is being evaluated, exclude that route from any
  pooling/covariate/training context (EXP-3/4/5); EXP-5 is leave-route-out
  by construction.
- Largest pool is ~3.3M rows — everything fits in RAM as float64.
  ~7k total fits at B=50; keep EXP-1/2 fits ≤ ~10s (they are), batch
  EXP-3's MCMC per draw (one fit serves all levels).
- Cliff test: two draws of 24,776 and 25,376 benigns from any ≥200k pool
  (these exact sizes are PE's historical min_sample_score straddle; any
  pair straddling 25,000 works).

## References

- Velthoen, Cai, Engelke, Zhou — *Gradient boosting for extreme quantile
  regression* (gbex), Extremes 2023. arxiv.org/abs/2103.00808
- Pasche, Engelke — *EQRN: extreme quantile regression neural networks*
  (flood-risk application).
- Coles — *An Introduction to Statistical Modeling of Extreme Values*
  (penalized-likelihood GPD; threshold stability diagnostics).
- Harrell, Davis — *A new distribution-free quantile estimator*, Biometrika
  1982.
- Scarrott, MacDonald — *A review of extreme value threshold estimation and
  uncertainty quantification*, REVSTAT 2012.
- NIST FRVT methodology — the "more data via pairing" exemplar for measured
  FMR at 1e-6; the reason §Oracle exists instead of trusting any model.
