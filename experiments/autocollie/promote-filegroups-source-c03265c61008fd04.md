# Promote REJECTED — `c03265c61008fd04` on `filegroups/source`

Generated 2026-06-13T18:31:53Z

AUC regressed at full-train: 0.9983 -> 0.9962

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9991)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `c03265c61008fd04` | `188b379f99798867` | `1c0607224b3f4a2d` |
| PR AUC | 0.9991 | 0.9968 | 0.9968 |
| ROC AUC | 0.9983 | 0.9962 | 0.9962 |
| F1 | 0.9821 | 0.9724 | 0.9733 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9983 -> 0.9962
