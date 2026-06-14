# Promote REJECTED — `956e522f2c6a5ae2` on `filegroups/scripts`

Generated 2026-06-13T20:25:31Z

AUC regressed at full-train: 0.9979 -> 0.9962

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9981)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `956e522f2c6a5ae2` | `7989d9961fd36463` | `3a4d5f3fc9749bd0` |
| PR AUC | 0.9981 | 0.9966 | 0.9968 |
| ROC AUC | 0.9979 | 0.9959 | 0.9962 |
| F1 | 0.9787 | 0.9692 | 0.9670 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9979 -> 0.9962
