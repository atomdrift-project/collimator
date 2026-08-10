# FP-Curve Estimation: Build + Results

Status: EXPERIMENTS RUN (2026-08-03). Implements `FP_CURVE_PROPOSAL.md`.
Nothing here touches a shipped bundle.

## What exists now

| path | what it is |
|---|---|
| `scripts/fp_curve_estimators/base.py` | the common estimator API (§Common estimator API), logit/level conversions, Harrell-Davis, order-statistic bands, saturation detection |
| `scripts/fp_curve_estimators/{b0,exp1..exp5}*.py` | the baseline and all five experiments |
| `scripts/fp_curve_estimators/{gpd,tailcurve,pools}.py` | shared GPD primitives, the body+tail composition, honest-score loading |
| `scripts/fp_curve_bench.py` | the scale-ladder backtest harness (also `--cliff`) |
| `scripts/fp_curve_report.py` | leaderboard, seven metrics, five gates |
| `scripts/fp_curve_synth.py` | synthetic-tail suite (absolute error bars at L0-1) |
| `scripts/fp_curve_all_routes.py` | all-routes application pass + diagnostics battery |

Reproduce:

```bash
.venv/bin/python scripts/fp_curve_bench.py --estimators b0,exp1,exp2,exp3,exp4,exp5 --draws 50 --jobs 12 --tag ladder
.venv/bin/python scripts/fp_curve_report.py out/experiments/fp_curves/ladder
.venv/bin/python scripts/fp_curve_bench.py --cliff --estimators b0,exp1,exp2,exp3,exp4,exp5 --draws 40
.venv/bin/python scripts/fp_curve_synth.py
.venv/bin/python scripts/fp_curve_all_routes.py --estimators b0,exp1,exp2,exp3,exp4,exp5
```

A full six-estimator ladder run (6 pools x 4 rungs x 50 draws x 44 levels =
317k scored points, 7,200 fits) takes ~3 minutes on 12 workers.

## Phase 0 status

- **General OOF pool: not landed yet.** `make azoth-publish-train` was still
  running at the time of these experiments (production-general phase, started
  08:25), so `out/models/azoth/general/threshold_scores.npz` does not exist.
  The harness detects its absence, warns, and proceeds; it will pick the pool
  up automatically as the deepest teacher once the run finishes. L21-22 is
  therefore still aggregate-only, exactly as the proposal anticipated.
- **Specialist floors: confirmed honest.** All 73 routes have full-route OOF
  pools; counts and floors re-verified at run time and they match the
  proposal's table (pe 205,094 / ~488; ruby 176,786 / ~566; gem 2,540 /
  ~39,370).

## Deviations from the proposal, and why

1. **EXP-3 uses empirical-Bayes MAP + Laplace, not NUTS/SVI.** numpyro/jax
   are not in the venv and would be a large dependency for a two-parameter
   posterior. The hierarchy is unchanged (global -> filegroup -> route,
   DerSimonian-Laird between-route variance, closed-form family shrinkage);
   only the inference engine differs. The API is untouched, so a sampler can
   be dropped in behind it.
2. **EXP-5 uses sklearn's GBM, not LightGBM.** The harness forks its workers;
   an OpenMP thread pool created by training in the parent deadlocks every
   child. This cost an hour to find and is worth remembering.
3. **The shape prior is measured, not assumed.** Fitting all 73 full pools
   put the fleet's GPD shape at median -0.165 (quartiles -0.32 / 0.00). The
   well-determined routes (large, non-atom tails) sit at -0.15 +/- 0.12, and
   that is what EXP-2's penalty and EXP-3's fallback use.
4. **Metric 1 is scored on FP counts summed over draws**, not on per-draw
   deviances averaged. That is what the proposal's own L21-22 argument
   implies ("the aggregate over B>=50 draws still detects calibration bias"),
   and a mean of per-draw deviances is dominated by single blown-up draws.

## Findings that change the problem statement

### 1. Twelve of 73 routes have a hard FP floor no estimator can beat

Benign files whose float32 probability is exactly 1.0 — the model has
saturated. No threshold excludes them without also excluding every saturated
malware sample, so the route's FP rate cannot go below `count/n`:

| route | benign | saturated | implied floor (FP/100M) |
|---|---|---|---|
| filetypes/plist | 97,587 | 1,026 | 1,051,370 |
| filetypes/deb | 23,528 | 762 | 3,238,694 |
| filetypes/rust | 321,421 | 464 | 144,359 |
| filetypes/java_class | 1,702,485 | 422 | 24,787 |
| filetypes/text | 296,301 | 333 | 112,386 |
| filetypes/makefile | 60,768 | 294 | 483,807 |
| filetypes/json | 227,366 | 293 | 128,867 |
| filetypes/png | 450,537 | 171 | 37,955 |
| filetypes/markdown | 120,647 | 53 | 43,930 |
| filetypes/c | 1,537,043 | 26 | 1,692 |
| filetypes/swift | 43,153 | 10 | 23,173 |
| filegroups/media | 794,870 | 1 | 126 |

For plist, deb, rust, text, makefile, json, png, markdown the **entire deploy
grid (L0-L25000) is unreachable** — the route FPs at every level the grid can
name. This is a model/calibration problem, not an estimator problem, and no
curve estimator can fix it; what an estimator *can* do is refuse to claim
otherwise. Every curve now clamps at the atom and emits
`saturation_floor_per_100M` + `saturation_limited` on affected rows.

### 2. Several routes' benign tails are quantisation atoms, not tails

`filetypes/c` has 14,448 of its top 15,370 benign scores tied at one value
(p=0.0026); `java_class`, `text`, `json`, `png`, `portable` and `media` are
similar. Those routes' "tail shape" is not estimable: their measured rise per
decade is exactly 0. This is what inflates the fleet-wide shape spread
(sd 0.30) relative to the routes that have real tails (sd 0.12), and it is
the real-data version of the proposal's "discrete atoms" adversarial shape.

An early guard that clamped on *any* top-of-sample tie collapsed those routes
onto an interior atom and produced a ~1% FP rate at every level — caught by
the harness before it went anywhere, which is the validation loop working.

### 3. The incumbent's 25k cliff is real and large

Metric 6, fitting at n=24,776 vs n=25,376 draws of the same pool (40 draws
each):

| estimator | median cliff z | max cliff z | median threshold jump (logit) |
|---|---|---|---|
| **b0** | **8.7 – 19.3** | **140.8** | **1.68 – 11.34** |
| exp1 | 0.19 – 1.75 | 1.75 | 0.02 – 0.93 |
| exp2 | 0.07 – 1.18 | 1.62 | 0.01 – 1.10 |
| exp3 | 0.16 – 1.26 | 1.60 | 0.03 – 1.10 |
| exp4 | 0.09 – 2.44 | 2.70 | 0.02 – 1.26 |
| exp5 | 0.61 – 1.87 | 2.52 | 0.00 – 0.88 |

A z of ~1 is sampling noise. B0 moves its threshold by up to 11 logits across
a 600-sample difference in pool size. Every replacement passes; the incumbent
fails by two orders of magnitude.

## Leaderboard (ladder backtest)

6 teacher pools, rungs m ∈ {800, 2500, 25000, 200000}, 50 draws, 44 levels.
Small rungs weighted 2x. Full table: `fp_curve_report.py`.

| estimator | metric 1 (Poisson dev, aggregated) | median abs log10 rate error | signed bias | dead predictions | coverage | mono violations | dial resolution |
|---|---|---|---|---|---|---|---|
| exp5 ladder-learned | **32,119** | 0.841 | +0.04 | 35.8% | 0.877 | 0.02 | 1.00 |
| exp4 boosted-tail | 43,839 | 0.762 | +0.04 | 33.4% | 0.814 | 0.00 | 1.00 |
| exp3 pooled-tail | 62,793 | **0.721** | +0.22 | 23.3% | 0.828 | 0.00 | 1.00 |
| exp2 logit-gpd | 70,088 | **0.715** | +0.23 | 22.6% | 0.822 | 0.00 | 1.00 |
| exp1 smooth-interp | 29,033,085 | 1.503 | +1.50 | 0.0% | 1.000 | 318.8 | 0.21 |
| b0 incumbent | 356,409,139 | 2.495 | +2.50 | — | 1.000 | 200.4 | 0.56 |

By rung (median |log10 realized/claimed FP rate| — lower is better):

| estimator | m=800 | m=2500 | m=25000 | m=200000 |
|---|---|---|---|---|
| b0 | 4.30 | 3.87 | 1.08 | 0.48 |
| exp1 | 2.73 | 2.05 | 1.19 | 0.47 |
| exp2 | 1.05 | 0.77 | 0.60 | 0.47 |
| exp3 | 1.02 | 0.79 | 0.60 | 0.48 |
| exp4 | 1.16 | 0.89 | 0.61 | 0.47 |
| exp5 | 1.12 | 1.06 | 0.75 | 0.49 |

By named level band (median |log10 rate error|):

| estimator | L0-1 | L21-22 | L250-300 | L1000+ |
|---|---|---|---|---|
| b0 | 2.78 | 2.89 | 2.98 | 2.13 |
| exp1 | 2.91 | 2.68 | 1.88 | 0.62 |
| exp2 | 0.76 | 0.84 | 0.94 | 0.42 |
| exp3 | 0.69 | 0.88 | 0.96 | 0.42 |
| exp4 | 0.03 | 0.46 | 1.02 | 0.52 |
| exp5 | 0.02 | 0.36 | 1.14 | 0.49 |

### The primary metric is gameable, and two estimators game it

Poisson deviance is asymmetric by construction: claiming L1 and delivering
**zero** FP costs almost nothing, while claiming L1 and delivering L5000
costs thousands. An estimator can therefore win metric 1 by predicting
thresholds that nothing fires on.

That is exactly what happens. At the deploy operating point (L25), fitting on
m=25,000 benigns and measuring on the full pool:

| estimator | realized level when L25 was claimed | median threshold (logit) | recall retained |
|---|---|---|---|
| b0 | 4,985 | 6.2 | 21.7% |
| exp1 | 7,389 | 5.7 | 25.9% |
| exp2 | 880 | 10.4 | 8.7% |
| exp3 | 1,114 | 10.7 | 8.2% |
| exp4 | 528 | 11.8 | 7.8% |
| **exp5** | **29** | **16.0 (the ceiling)** | **0.0%** |

EXP-5's near-perfect FP calibration is achieved by shutting the route off.
Over a third of its emitted thresholds (35.8%) fire on nothing at all. EXP-4
is a milder version of the same failure. The proposal's metric 3 (recall
error) and the `dead_frac` / `signed_log_ratio` columns added here are what
make it visible; ranking on metric 1 alone would have shipped it.

On the symmetric measure — how far the delivered FP rate is from the claimed
one, in either direction — the order reverses: **exp2 (0.715) ≈ exp3 (0.721)
< exp4 (0.762) < exp5 (0.841) ≪ exp1 (1.503) < b0 (2.495)**.

## Gates

| gate | b0 | exp1 | exp2 | exp3 | exp4 | exp5 |
|---|---|---|---|---|---|---|
| 1 measured-region fidelity | PASS | PASS | PASS | PASS | PASS | PASS |
| 2 strict monotonicity | FAIL | exempt (control) | PASS | PASS | PASS | FAIL (1 fit / 1200) |
| 3 cliff test | **FAIL** | PASS | PASS | PASS | PASS | PASS |
| 4 dial resolution | FAIL | exempt (control) | PASS | PASS | PASS | FAIL (same fit) |
| 5 CI coverage >= 85% | PASS* | PASS* | 0.822 FAIL | 0.828 FAIL | 0.814 FAIL | 0.877 PASS |

\* B0 and EXP-1 pass coverage trivially: their bands are 2.9-3.4 decades wide
in FP-rate terms (vs 0.5-1.1 for the GPD family), i.e. vacuous. Band width is
reported alongside coverage for exactly this reason.

EXP-5's single gate-2/4 failure is one fit out of 1,200, on `filetypes/c` —
the route whose top 1% is 94% a single quantisation atom.

**No estimator passes all five gates.** The GPD family misses coverage by
2-4 points; the learned estimators pass coverage but degenerate.

## Synthetic-tail suite (absolute error bars at L0-1)

Seven shapes: a body resampled from real `filegroups/scripts` benign scores,
spliced at the 99th percentile onto an analytic tail with a known survival
function, then clamped at the float32 score ceiling exactly as real routes
are. Truth is exact; results are reported per shape, never averaged.

Median |log10 realized/claimed FP rate|, all levels:

| estimator | atoms | contaminated | gpd_pure | heavy | mixture_bump | spliced_light | truncated |
|---|---|---|---|---|---|---|---|
| b0 | 2.94 | 2.98 | 3.00 | 3.39 | 2.99 | 3.02 | 3.00 |
| exp1 | 2.28 | 2.28 | 2.31 | 2.67 | 2.38 | 2.40 | 2.40 |
| exp2 | 1.15 | 1.37 | **1.06** | 2.29 | 3.85 | 0.92 | 6.30 |
| exp3 | 1.11 | 1.43 | 1.16 | 2.36 | 3.17 | 1.02 | 5.70 |
| exp4 | 1.57 | 1.25 | 1.11 | **2.29** | 5.69 | 1.15 | 7.32 |
| exp5 | **0.62** | 1.69 | 1.73 | 2.37 | **1.09** | **0.53** | 7.32 |

Fraction of predictions that fire on **nothing** — the threshold sits above
the distribution's entire support, so the route goes silent:

| estimator | atoms | contaminated | gpd_pure | heavy | mixture_bump | spliced_light | truncated |
|---|---|---|---|---|---|---|---|
| b0 / exp1 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| exp2 | 15.0% | 0.0% | 0.0% | 0.0% | 0.0% | 7.7% | **65.8%** |
| exp3 | 13.6% | 0.0% | 0.0% | 0.0% | 0.0% | **4.4%** | 54.4% |
| exp4 | 33.8% | 0.0% | 0.0% | 0.0% | 0.0% | 26.1% | 91.9% |
| exp5 | 9.8% | 0.0% | 0.0% | 0.0% | 0.0% | 14.1% | 89.9% |

Three things fall out of this:

1. **The anti-circularity rule earns its place.** EXP-2 is at its best on
   `gpd_pure` — literally its own assumption class — and its worst on
   `truncated`, where two thirds of its thresholds kill the route. Averaging
   across shapes would have hidden both.
2. **A hard tail endpoint breaks every extrapolator.** On `truncated` (the
   tail simply stops, xi = -0.45) the extrapolators overshoot the support
   54-92% of the time. This is not hypothetical: `truncated` is what a route
   whose scores saturate looks like from below.
3. **On the realistic shape (`spliced_light`), EXP-3 has the lowest dead
   fraction of any extrapolator (4.4%)** while sitting within 0.1 decades of
   EXP-2's accuracy — the shrinkage is buying stability, which is exactly
   what it was supposed to buy.

Signed bias at L0-1 by rung (negative = too strict, i.e. giving up recall):

| estimator | m=800 | m=2500 | m=25000 | m=200000 |
|---|---|---|---|---|
| b0 | +5.07 | +4.54 | +3.69 | +2.82 |
| exp1 | +5.25 | +4.70 | +3.84 | +2.97 |
| exp2 | +3.04 | +2.55 | +1.79 | +1.47 |
| exp3 | +3.52 | +3.41 | +2.03 | +1.47 |
| exp4 | **-5.70** | +2.43 | +2.18 | -0.14 |
| exp5 | **-5.70** | -2.91 | +2.06 | +1.79 |

B0 and EXP-1 are 3-5 decades too *loose* at L0-1 at every scale — they
deliver ~100,000x the FP rate they promise. EXP-2/EXP-3 cut that to 1.5-3.5
decades and never overshoot into silence. EXP-4/EXP-5 flip sign at small m:
they go dead instead.

## All-routes application pass

Every candidate fitted on all 73 routes' full OOF pools, with the diagnostics
battery. Results: `out/experiments/fp_curves/all_routes/per_route.csv`.

| estimator | routes | hard failures | rate | high-volume failures | review flags | saturated routes |
|---|---|---|---|---|---|---|
| b0 | 73 | 48 | 65.8% | 7 | 0 | 12 |
| exp1 | 73 | 63 | 86.3% | 12 | 0 | 12 |
| **exp2** | 73 | **0** | **0.0%** | 0 | 0 | 12 |
| **exp3** | 73 | **0** | **0.0%** | 0 | 9 | 12 |
| **exp4** | 73 | **0** | **0.0%** | 0 | 0 | 12 |
| exp5 | 73 | 1 | 1.4% | 1 | 0 | 12 |

"Hard failures" are monotonicity, dial resolution, CP-flag consistency, or a
fit that threw. Family-shape outliers are reported separately as review flags
because the proposal asks for them to be *reviewed*, not treated as failures.

B0 fails 48 routes and EXP-1 fails 63 — both from exactly the behaviour the
proposal predicted (B0's absolute-FP staircase, EXP-1's clamp), which is why
EXP-1 is exempt as the control. EXP-5's single failure is `filetypes/c`, the
94%-atom route.

EXP-3's nine review flags are informative rather than embarrassing: they are
`json` (z=-10.9), `deb` (-6.0), `ruby` (+4.0), `java_class` (+3.9),
`github_actions` (+3.8), `source` (+3.3), `xlsx` (+3.2), `rust` (+3.1),
`ole` (+3.0) — i.e. the shrinkage diagnostic is picking out precisely the
routes whose benign tail is a saturated or quantised atom rather than a tail.
It is finding the routes from Findings 1 and 2 without being told about them.

## Strict-end audit — all 21 scorable route models, L0-L100

`scripts/fp_curve_audit.py` over `out/experiments/fp_curves/audit-all`
(21 route models with >=200k benigns — the only ones deep enough to score —
x 4 rungs x 50 draws, 1.04M points). Scored at each model's **largest
available rung**, which is the closest proxy for how it is actually
calibrated. Accuracy is |log10(realized/claimed FP rate)| summed over the
band; 0 is perfect, 1.0 means an order of magnitude out.

The 21 split cleanly into two populations:

**14 models where accuracy is achievable:**

| estimator | median error (decades) | within 1 decade | median silenced |
|---|---|---|---|
| **exp3** | **0.46** | **12 / 14** | 20% |
| exp2 | 0.64 | **12 / 14** | 6% |
| exp4 | 0.82 | 9 / 14 | 1% |
| exp5 | 2.14 | 4 / 14 | 0% |
| b0 | 1.54 | **0 / 14** | 0% |
| exp1 | 1.65 | **0 / 14** | 0% |

**7 saturation-bound models** (media, c, java_class, json, png, rust, text) —
every estimator scores *identically*: median 3.1 decades, 100% of the band
silenced. The benign atom at p=1.0 sets the answer; the estimator is not a
factor. This is Finding 1 measured end-to-end.

Smoothness in the band (total variation of d(logit t)/d(log level), median
over models): exp3 **0.06**, exp4 0.13, exp2 0.14, exp5 0.00-3.7 (variable),
b0 **71.1**. Strict monotonicity and a fully resolving dial: exp2, exp3, exp4
and exp5 pass on all 21 models; b0 and exp1 fail on most.

There is a scale crossover worth knowing. Median band error by rung:

| estimator | m=800 | m=2,500 | m=25,000 | m=100,000 |
|---|---|---|---|---|
| exp2 | 2.37 | 2.35 | 1.44 | 0.73 |
| exp3 | 2.56 | 2.59 | 1.50 | **0.68** |
| exp4 | 2.60 | 2.29 | 1.51 | 0.82 |
| exp5 | **2.15** | **2.18** | 2.60 | 2.36 |
| b0 | 4.49 | 3.94 | 2.17 | 1.55 |

EXP-5 is the best estimator for genuinely tiny samples and the worst at
deployment scale — the reverse of every other method. It was trained on
ladder pairs dominated by deep extrapolation, and that is what it is good at.

**Verdict: EXP-3, with EXP-2 as the near-tie alternative.** EXP-3 has the
lowest strict-end error and the smoothest curve; EXP-2 matches its hit rate
and silences a third as much of the band. Both beat the incumbent by ~1.1
decades in the band, and both are strictly monotone with a full dial on every
model. Neither b0 nor exp1 lands within an order of magnitude on a single
model at the strict end.

**The caveat that limits this result:** the band aggregate is dominated by its
loose end (L50-L100 carry most of the expected FP), so "within a decade in
L0-L100" does **not** mean L1 is within a decade. The synthetic suite, which
is the only place L0-1 has exact truth, puts EXP-2/EXP-3 at 2.2-2.7 decades
of error there on realistic shapes. The strict end of the strict end remains
unverified and is still the weakest claim in this work.

## Outcome (2026-08-03)

**Superseded by what shipped.** The recommendation below (EXP-3b, graphing
path only) was overtaken by two later results: EXP-8b — anchoring on measured
FP counts with a one-decade extreme slope — matched EXP-3b on accuracy at 70x
less cost and beat it decisively at L1 (0.252 vs 0.743 median error, 15/15
routes within a decade vs 10/15); and the resolution-adjusted level scale
removed nearly all of the extrapolation the estimators existed to perform.
What landed in `collimator.thresholds` is EXP-8b on the adjusted scale, with
the 25k low-volume regime deleted. See `LEVELS.md` for the contract.

Retired along the way, with evidence: EXP-3c (ladder-calibrated correction —
centred the bias, worsened the variance), EXP-6 (median ensemble — no gain
over its members), EXP-7/7b (log-linear and borrowed-curvature — 35-94x too
strict, because a body-fitted slope ignores tail flattening), and the
cross-model ensemble curve (bootstrap showed blending unreliable at the
strict end and `max` actively harmful).

## Recommendation (historical)

1. **Do not ship EXP-5 or EXP-4** despite their metric-1 wins. They buy
   calibration with silence.
2. **EXP-3 (or EXP-2 — they are within noise of each other) is the candidate
   worth continuing with.** Best symmetric calibration, zero shape-gate
   failures fleet-wide, ~1.8 decades better than the incumbent below the
   floor, and the 25k cliff gone. EXP-3 is preferable to EXP-2 despite the
   near-tie because the hierarchy is what makes a route with no usable tail
   of its own (gem, rtf, lnk, applescript) inherit something defensible, and
   it carries a shrinkage diagnostic that flags when a route disagrees with
   its family.
3. **It is not ready for the deploy path.** Coverage is 2-3 points short of
   the gate, and ~23% of its sub-floor predictions still fire on nothing. The
   honest rollout is the narrow one the proposal already scoped: emit the
   curve for the graphing consumers (`../website` / `../gauntlet`) with
   `model_extrapolated`, `cp_floor_per_100M` and `saturation_floor_per_100M`
   on every row, keep deploy gates and promote logic on measured quantiles,
   and let the production backtest accumulate before revisiting.
4. **Fix the saturated routes first.** Eight routes cannot honour *any* level
   in the deploy grid because the model scores some of their benigns at
   exactly 1.0. No estimator can help them, and a curve that implies
   otherwise is worse than no curve. That is a model-side task and it
   outranks further estimator work.

## What is left

- Re-run the ladder with the general OOF pool once `azoth-publish-train`
  lands it, and upgrade L21-22 from aggregate-only to direct verification.
- Coverage: the GPD bands under-cover by 2-4 points and switching from the
  penalized posterior to the observed information moved it by <1 point, so
  the shortfall is model misspecification at depth rather than a covariance
  scaling issue. A predictive band that mixes over the *threshold-selection*
  step (u is chosen from the same data) is the obvious next thing to try.
- The `pe`/`ruby`/`gem` deep dives named in the proposal are runnable now via
  `fp_curve_all_routes.py --routes`, but they cannot be *scored* (no deeper
  pool to verify against) — they are curve-shape inspections only.
