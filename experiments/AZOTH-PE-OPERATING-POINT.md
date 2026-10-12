# PE operating point: out-of-time backtests

Status: 2026-09-15. Harness: `src/collimator/backtest.py`,
`scripts/azoth_backtest.py`, `tests/test_backtest.py`, `make azoth-backtest`.

## The question

`filetypes/pe` publishes 59.54% recall at L25. Production, measured from
`samples.lvl` over the 30 days to 2026-09-15, catches 17.97% of labeled-bad PE
and fires on 1,148 benign PE per million. The published number and the
deployed behaviour are not the same number, and nothing in the pipeline
measured the difference, because every operating-point metric collimator
reports is fitted and evaluated on the same benign pool.

## The method

An operating point is fitted on benign rows ingested up to a cutoff
(`samples.created_at`) and measured on rows ingested after it. Fit and eval
populations are disjoint by construction — `backtest()` raises if they overlap
unless `allow_overlap=True` is passed for a deliberate in-sample baseline.

The harness reads `score_table.npz`, the same per-row route scores the policy
search consumes, so a backtest scores exactly the rows the shipped policy was
chosen on. No retraining, no feature extraction; a run is seconds once the
metadata cache is warm.

**`validate` runs first and is not optional.** It refits the L1 joint-OR
thresholds and compares them to what `azoth_route_policy_search.py` shipped in
`route_policies.json`. On 2026-09-15 all three PE routes matched to six
decimals (`general` 0.999758, `filegroups/native` 0.999692, `filetypes/pe`
0.999590). If that block reports DRIFT, every number below it is void.

Two harness bugs were caught by that discipline and are now regression-tested:

* A single `max`-combined score is not the shipped decision rule. joint-OR
  catches 26% where one max threshold catches 4.8%, because a row the
  specialist is confident about does not have to out-score the general model's
  tail. `kind="joint_or"` is the default.
* NaN route scores (57 rows of 1.9M unscored by `filegroups/native`) sorted
  into the benign tail and produced a NaN threshold, which silently dropped
  that route out of the OR.

## Results

All at L25, `joint_or`, routes `general` + `filegroups/native` +
`filetypes/pe`, slice = 1,904,114 rows (1,638,538 malware / 265,576 benign),
ingest span 2026-04-24 .. 2026-09-14.

### 1. The published number is in-sample; the gap is ~5x

| | recall | FP | FP/M |
|---|---:|---:|---:|
| in-sample (what we publish) | 37.61% | 3 | 13.1 |
| out-of-time (what deploys) | 7.86% | 1 | 27.6 |

−29.75pp. This is not the September archival import: excluding feeds `win32`,
`win9x` and `msil` entirely, out-of-time recall is 6.46% and the walk-forward
holds it flat at **5.92% – 7.12% at every cutoff from 90 days back**. The
regression predates the import by at least a quarter.

### 2. Pool hygiene buys recall at zero measured FP cost

Suspect benign cohorts are dropped from the FITTING pool only; the evaluation
pool is untouched.

All feeds (260,355 eval malware), paired bootstrap vs the unfiltered pool,
2,000 resamples:

| fitting pool | n | out-of-time recall | FP/M | Δrecall (95% CI) |
|---|---:|---:|---:|---|
| all benign (today) | 229,386 | 7.86% | 27.6 | — |
| drop carved sub-files | 143,209 | 8.88% | 27.6 | +1.02pp [+0.98, +1.07] |
| drop suspect feeds | 142,784 | 12.26% | 27.6 | +4.41pp [+4.33, +4.49] |
| drop both | 56,607 | **13.10%** | 27.6 | **+5.24pp [+5.15, +5.33]** |

The same intervention on the drift-only view (archival feeds excluded, 2,060
eval malware — the number that matters, because it is not carried by the
import):

| fitting pool | out-of-time recall | FP/M | Δrecall (95% CI) |
|---|---:|---:|---|
| all benign (today) | 6.46% | 0.0 | — |
| drop carved sub-files | 6.99% | 0.0 | +0.53pp [+0.24, +0.87] |
| drop suspect feeds | 7.91% | 0.0 | +1.46pp [+0.96, +1.98] |
| drop both | **8.40%** | 0.0 | **+1.94pp [+1.37, +2.54]** |

Every CI excludes zero (p < 0.0001), and the false-positive count is unchanged
in both views. +30% relative recall on genuine drift, +67% overall, for free.

`carved` is a row property: extracted from a parent, so the benign label was
inherited rather than observed. The suspect feeds are
`pe-machine-learning-dataset` (32.6% of the benign PE eval pool on its own;
one member carries `max_crit=5, suspicious_count=16` while labeled benign) and
`enron-xls` (PE attachments carved out of the Enron email corpus).

### 3. L25 cannot be extrapolated to its literal rate on this pool

PE's 265,576 benigns resolve a first false positive at 3.77 FP/M. L25's
literal rate is 0.25 FP/M — **1.18 decades past the last measurement**.

`extrapolation_error` fits on a subsample small enough that a target rate is
below *its* 1-FP floor, then measures the realized rate on the held-out
remainder. Across 0.3–1.5 decades of reach, on all three routes, the realized
rate is a median **0.0–0.58x** of requested with a p05..p95 spanning roughly
0.0x to 10x. The extrapolated threshold is biased strict and its error bar is
two to three orders of magnitude wide — at 1.5 decades on `filetypes/pe` and
`general` the median realized rate is 0.

Applying the literal rate directly (`--estimator true_rate`) costs what that
bias implies: out-of-time recall falls 7.86% → 1.24% for 0 observed FP.

Caveat, stated because it cuts against the conclusion: distance and fit size
are coupled in this design — reaching 1.2 decades means fitting on ~1,500
benigns, which has far less tail information than the real 265,576-benign
pool. The test therefore understates the estimator. It cannot be decoupled:
validating a rate the full pool cannot measure is not possible with the full
pool. That is itself the finding — **the only thing that makes L25 honest on
PE is ~4M benign PE files** (0.25 FP/M × 4M = 1 expected FP).

### 4. The operating point is unstable across refits

`azoth` shipped 37 bundles in the 90 days to 2026-09-15, each re-deriving this
threshold from whatever benign pool existed that night. Refitting on 80%
resamples of the pool moves realized FP/M across 11.30..18.83 and recall
across 26.97%..38.64% — a ±6pp recall swing from resampling alone, before any
model change.

### 5. Policy search leaves the loose end of the grid unused

Separate from the harness, verified directly against `route_policies.json`:
`_is_over_target` (`scripts/azoth_route_policy_search.py:1159`) compares
`fp_per_100M` against `target_per_million`, a 100x unit mismatch that makes
the intended "allow 10x target" behave as "allow target/10". It predicts the
selected FP count on 41 of 41 PE levels. PE at L10000 ships 26.26% where 26 FP
of budget would buy 65.35%; at L25000, 39.16% where 663 FP would buy 72.99%.

It costs PE **nothing at L25** — both allowances round to 0 FP on 265k
benigns — so it is not the cause of the headline number, but it is why the
42-point grid has three distinct operating points instead of 42.

## What this says to do

1. Fix the `_is_over_target` unit mismatch. One line, free, and it makes the
   loose end of the grid mean something.
2. Exclude carved sub-files and the two suspect feeds from the benign
   *calibration* population. +5.24pp out-of-time at unchanged FP.
3. Stop publishing `recall_at_25_per_100M` for slices whose
   `min_observable_per_100M` exceeds 25 — report the measured anchor
   (`recall_at_0fp` / `recall_at_1fp`) instead.
4. Add the out-of-time backtest to the deploy gate so this regression can
   fail a publish rather than being discovered a quarter late.
5. Acquire benign PE in bulk. Nothing else makes L25 mean 0.25 FP/M on this
   route, and no estimator can substitute for the measurement.

## Harness limitations, stated

* `joint_or` here fits each route independently at the level, which is exactly
  the shipped `joint_or_at_fp_0` construction but NOT the coordinate-descent
  redistribution the policy search does at non-zero FP budgets.
  `azoth_route_policy_search.py` stays the authority on shipped thresholds;
  `validate` is what keeps the two honest.
* Ingest time (`created_at`) is when hopper first saw a file, not when it
  appeared in the world. A bulk import of old files looks "new" to this split
  — which is why `--exclude-feed` exists and why every headline result above
  is quoted both ways.
* The out-of-time malware window is small once archival feeds are removed
  (~2k rows at a 30-day holdout). Use the paired CI, not the point estimate.

## Reproducing

```bash
make azoth-backtest ROUTE=pe
make azoth-backtest ROUTE=pe BACKTEST_ARGS="--exclude-feed win32 --exclude-feed win9x --exclude-feed msil"
make azoth-backtest ROUTE=pe BACKTEST_ARGS="--experiment pool-hygiene --level 3000"
```
