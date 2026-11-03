# Severity levels: the shared Collimator, Azoth, and Scan contract

Updated 2026-11-01. This is the authoritative level definition for Collimator’s
training and evaluation, Azoth’s model bundles, and Scan’s `-l` option and API.
It retains the existing `L−1` convention. No model thresholds change merely
because the documentation changes.

## Definition

A level controls the false-positive allowance for a pool of **benign files**.
For a pool containing `N > 0` benign files:

```text
L0:     continuous allowance = 0
L > 0:  continuous allowance = 1 + (L - 1) * N / 100_000_000
```

The integer FP-count budget is the floor of that allowance, capped at `N`.
A pool with no benign observations has no measurable allowance.

- **L0:** zero observed false positives in calibration.
- **L1:** one false positive in the pool, with no additional rate allowance.
- **L25:** one false positive plus an estimated additional **24 per 100 million
  benign files**. “One FP plus approximately 25 per 100 million” is shorthand;
  the exact increment is 24 because the first FP is anchored at L1.
- **L1000:** one false positive plus an estimated additional 999 per 100 million.

L25 is the deployment default. Lower levels are stricter; higher levels allow
more false positives in exchange for potentially more detections. L0 is a
separate zero-observed-FP case, not a substitution into the positive-level formula.

The initial FP belongs to the calibration/evaluation decision pool. It is not
an extra FP per component model, scan invocation, archive, or future block of
100 million files. `N` refers to the benign sample population used to calibrate
or evaluate that decision, not the number of files in a user's scan command.

| Benign files in the pool | L1 allowance | L25 continuous allowance | L25 integer budget |
|---:|---:|---:|---:|
| 2,540 | 1 | 1.0006096 | 1 |
| 1,000,000 | 1 | 1.24 | 1 |
| 4,000,000 | 1 | 1.96 | 1 |
| 100,000,000 | 1 | 25 | 25 |

Fractional allowances describe the target curve; an observed count is always
an integer. Several levels can therefore share the same count budget. Tied
model scores can also prevent spending exactly that budget: it is an allowance,
not a requirement to produce a particular number of errors.

## Rates, estimates, and observations

For positive levels, the equivalent nominal rate per 100 million is:

```text
first_FP_rate = 100_000_000 / N
nominal_rate_per_100M = first_FP_rate + L - 1
```

The level label alone is not a literal population FP rate. At L25, one FP in a
2,540-benign pool corresponds to about 39,370 observed FP/100M, while one FP in
a million-benign pool corresponds to 100 observed FP/100M. Neither observation
establishes the future rate. At exactly 100 million benigns the allowance and
level number coincide.

We aim to estimate the additional rate as accurately as possible, using
interpolation or extrapolation when sample resolution requires it. An
extrapolated estimate is not a measurement or a guarantee. Heavy extrapolation
must remain identifiable, with its sample size and uncertainty; it does not
remove the initial one-FP allowance or turn L25 into a literal 25-FP/100M target.

Reports must distinguish the requested level, benign count, allowed/observed FP
counts, observed FP rate, and uncertainty. A one-sided 95% exact binomial upper
bound is a separate statistical quantity, not the budget used for selection.
Those bounds assume independent, representative benign observations. Zero
observed FPs does not establish zero future risk, and there is no universal
“within 5–6×” accuracy guarantee for small filetypes.

## One allowance for the final decision

The deployed budget belongs to **one final filetype decision pool**. General,
group, and specialist models share it. Standalone calibration uses each model’s
own benign pool, but its thresholds do not create additive FP credits when
models are combined.

Policy search maximizes recall within the shared allowance on dev. Selection
counts the union of decisions from every level up to the requested level,
matching Scan’s runtime sweep. Two policies hitting different benign files
spend two FPs, even when each individually hits only one. Shared false positives
are counted once. This is a sequential search, not a global-optimality claim.

Test evaluates the frozen decisions using each test pool’s benign count; it
must not choose new thresholds. Repeatedly using test outcomes to select
configurations requires fresh confirmation data. An under-budget filetype does
not subsidize an over-budget filetype. All-empty policy grids are evaluated with
the runtime’s general fallback, not assumed to be inert.

Nightly reports FP overruns across the grid. They do not block installation by
default; detection regression and runtime validation gates remain mandatory.
For deployment and regression-recovery acceptance, only detection losses at
L0 through L25 can block. The deployment gate retains its configured recall
tolerances and net-improvement policy within that range. Check every saved
operating point in that inclusive range using the runtime's cumulative sweep. Detection changes above L25 remain reportable
but do not block acceptance. This does not relax calibration FP allowances.
`AZOTH_BUDGET_GATE_ARGS=--fail-on-budget` opts into the empirical FP-count gate.
`--budget-gate-level` selects a checkpoint, while `--budget-gate-max-level`
explicitly checks levels up to a ceiling. An L25 check does not silently impose
an L0 requirement of zero test FPs.

## Implementation and numerical limits

`collimator.thresholds.resolution_adjusted_fp_budget` implements the integer
allowance. `quantile_severity_threshold` maps requested levels to score cuts;
its legacy `target_per_million` argument carries `L / 100`, not the full
pool-adjusted FP rate. Serialized fields such as `target_per_100M` likewise
encode the nominal level; observed `fp_per_100M` is a different quantity.

The current standalone curve uses observed benign order-statistic anchors and
linear interpolation in log-rate/logit-score space. For positive levels it
applies the `first_FP_rate + L - 1` shift. Its strict-end continuation estimates
an extrapolation slope from the deepest decade of anchors. L0 is constrained
above the largest observed benign score using a float32 step so the exclusion
survives serialization. Final policy search can choose different score cuts
under the shared integer count allowance; the resulting frozen policy is what
Scan evaluates.

For untied scores, the k-th FP anchor maps to
`L = 1 + (k - 1) * first_FP_rate`. Ties, finite precision, and score saturation
can merge operating points, so neither distinct thresholds nor exactly k FPs
at every anchor are universal guarantees. A threshold above 1 can represent
an inactive probability rule; calibration and runtime fallback must agree on
that behavior. Saturated scores may require model changes rather than a better
curve fit.

Scan reads saved thresholds and policy grids; it does not extrapolate anew for
each scan. It reports the lowest level at which a file fires. Its suspicious
band is derived from the level table and does not change the level definition.

## Historical research

[FP_CURVE_PROPOSAL.md](FP_CURVE_PROPOSAL.md) and
[FP_CURVE_RESULTS.md](FP_CURVE_RESULTS.md) preserve dated estimator experiments,
including literal-rate alternatives. Their numeric results and corpus sizes
are historical evidence, not the current level definition or a guarantee for
an installed bundle. [METHODOLOGY.md](METHODOLOGY.md) defers to this contract
for severity-level semantics.
