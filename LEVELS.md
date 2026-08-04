# Severity levels: what they mean and how they are computed

Status: 2026-08-03. Supersedes the level description in METHODOLOGY.md
§"L0..L10000 severity tiers". Implemented in
`collimator.thresholds.quantile_severity_threshold`; experiments and evidence
in `FP_CURVE_RESULTS.md`.

## The contract

A level is a **false-positive budget on benign files, expressed per 100
million — resolution-adjusted to the route it is applied to**:

    true_rate = requested_level + floor_level - 1

where `floor_level = 1e8 / n_benign` is the rate of that route's first false
positive. Three consequences define the contract:

* **L1 is the first false positive, on every route.** Not "1 per 100M" — one
  actual observed FP. L0 is one step stricter along the same curve and admits
  zero.
* **The k-th false positive sits at `L(1 + (k-1) * floor_level)`.** On ELF
  (floor 160) FP2 is at L161; on general (floor 8) FP2 is at L9.
* **At 100M benigns the floor is 1 and the mapping is the identity.** This is
  the true per-100M rate scale, quantised to the resolution a route actually
  has — not a different unit.

The cost, stated once: the same level is a different true rate on different
routes (L25 is 31.7/100M on general, 39,394/100M on gem). Comparability moves
from the label to the false-positive count. That is deliberate. The
alternative is claiming a rate a route cannot deliver, which is what the rule
before 2026-08-03 did by a median factor of ~945x.

## Three floors, per route

Every route has three distinct limits. Confusing them is the source of most
of the trouble in this area.

| floor | definition | example (PE, 205,094 benigns) |
|---|---|---|
| **1-FP floor** | `1e8 / n_benign` — the strictest level at which one observed false positive exists | L488 |
| **certifiable floor** | Clopper-Pearson 95% bound with zero observed FP: `1e8 * (1 - 0.05^(1/n))` | L1,461 |
| **saturation floor** | `1e8 * (benigns scored p=1.0) / n` — unreachable at any threshold | L0 (PE is not saturated) |

Fleet values:

| route | benign | 1-FP floor | 95% certifiable | saturated |
|---|---|---|---|---|
| general | 12,945,343 | L8 | L23 | no |
| filegroups/scripts | 2,970,762 | L34 | L101 | no |
| filetypes/elf | 626,474 | L160 | L478 | no |
| filetypes/pe | 205,094 | L488 | L1,461 | no |
| filetypes/ruby | 176,786 | L566 | L1,695 | no |
| filetypes/npm | 6,195 | L16,142 | L48,346 | no |
| filetypes/gem | 2,540 | L39,370 | L117,873 | no |
| filetypes/plist | 97,587 | L1,025 | L3,069 | **L1,051,370** |

Eight routes (plist, deb, rust, text, makefile, json, png, markdown) score
some benign files at exactly p=1.0. For those the *entire* deploy grid is
unreachable: they false-positive at every level the grid can name, and no
estimator can change that. It is a model problem, not a threshold problem.

## The "at least 1 FP" rule

L0 means *no* benign fires. Every level above L0 admits at least one false
positive — otherwise L0 and L1 would be the same threshold and the strict end
of the dial would carry no information.

The rule before 2026-08-03 implemented this as a *clamp*
(`_fp_budget_for_rate`: `max(1, floor(n * rate))`), which forced a route to
spend one false positive on a level it could not resolve. On PE, L25 budgets
0.051 expected FP, the clamp rounded it to 1, and 1 FP in 205,094 *is* L488 —
so PE's entire L0-L50 range shipped the same threshold while reporting 31%
recall against a rate 20x looser than the label.

The resolution-adjusted scale gets the same guarantee without the clamp: L1
*is* the 1-FP anchor, so every level from L1 up admits at least one false
positive by construction on every route, at or below the observed maximum.
Only L0 sits above the data, by one step, and it admits zero. Verified across
all 74 routes: 0 invariant violations.

## How a curve is built (EXP-8b)

Chosen on measured accuracy at L1 and L25 across 15 non-saturated routes:
median error 0.62 decades against the incumbent's 1.88, best worst-case of
any candidate, and the only estimator centred rather than biased loose.
Full comparison in `FP_CURVE_RESULTS.md`.

1. **Anchors are measurements.** The k-th largest benign score IS the
   threshold admitting exactly k false positives, at level `k * 1e8 / n`.
   Anchors are taken at k = 1..10 and then geometrically out to 5% of the
   pool.
2. **Between anchors: interpolation.** Shape-preserving monotone (PCHIP) in
   (log level, logit threshold). No model, no distributional assumption.
3. **Below the 1-FP anchor: one line.** Slope measured over the deepest
   decade of anchors (1 to 10 FP) and extended. That window matters: a slope
   fitted over the *body* (5-5000 FP) extrapolates 35-94x too strict, because
   benign tails flatten faster than their bodies imply.
4. **L0 is one step further along the same line**, so there is no
   discontinuity between L0 and L1.

Everything is in logit space; thresholds convert back at emission. The curve
is strictly monotone and smooth by construction (measured total variation
0.000), and it is capped at the float32 probability ceiling because no
threshold above p=1.0 is representable.

## What each emitted row carries

| field | meaning |
|---|---|
| `level` | the requested budget, per 100M |
| `threshold` | the score at or above which a file fires |
| `model_extrapolated` | true below the 1-FP floor — this row is a claim, not a measurement |
| `cp_floor_per_100M` | the tightest rate this corpus can certify at 95% |
| `saturation_floor_per_100M` | the rate imposed by benigns scored p=1.0 |
| `saturation_limited` | true when the requested level is below that floor |

A consumer that needs a promise should read `cp_floor_per_100M`; a consumer
that wants a dial reads `threshold`. The level never silently becomes a
guarantee it cannot back.

## Consequence for the suspicious tier

`scan` derives the suspicious threshold as a **level-table lookup** at
`min(max_grid_level, 3000)` (`capped_suspicious_level`), so nothing breaks
mechanically — it reads whatever the table says. But the separation between
hostile and suspicious is now route-relative too.

On a route whose floor exceeds the grid span (n < 4,000 benigns, so
`floor_level > 25000`), the **entire** L0-L25000 grid lives between that
route's 1st and 2nd false positive. Every level returns the same single FP,
and hostile and suspicious collapse onto thresholds separated only by
interpolation within one FP gap. Roughly 15 routes are in that state today:
applescript, chrome-manifest, chrome_manifest, docx, xpi, rtf, lnk, xlsx,
gem, nupkg, crx, ooxml, vsix, vbs, pkg-info.

This is honest — those corpora genuinely cannot resolve a second operating
point — but it is a behaviour change for consumers that bucket on
`l > critical_level` (promoter, prism, hopper). Growing those corpora is the
only fix.

## Verification

Two properties are cheap to check on any route and should gate any change:

1. **Anchor exactness** — at the k-th anchor the curve must produce exactly k
   false positives. EXP-8b passes by construction; a tail-model estimator
   anchored deeper (EXP-3b, anchored at 5 FP) fails at k=1, returning a
   threshold 1.56 logits above the highest benign that exists.
2. **Strict monotonicity and distinct thresholds** over the continuous grid,
   below the score ceiling.

The scale-ladder backtest (`scripts/fp_curve_bench.py`) verifies calibration
by subsampling deep pools and counting realized false positives on the full
pool. `scripts/fp_curve_audit.py` scores the strict end across every route
deep enough to be measured.

## Known limitations

- **Cross-route comparability is by FP count, not by label.** L25 means a
  different true rate on every route. Compare routes by how many false
  positives a level spends, not by the level number.
- **Below the 1-FP floor, accuracy is roughly half a decade** at deployment
  scale (median 0.62 for L1+L25) and degrades on small routes.
- **Saturated routes cannot honour any grid level** and need model work, not
  estimator work.
- **The general-model OOF pool (12.9M benigns, floor L8) landed 2026-08-03**
  and is the only route that can certify the L25 deploy point.
