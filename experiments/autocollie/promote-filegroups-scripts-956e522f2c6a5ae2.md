# Promote REJECTED — `956e522f2c6a5ae2` on `filegroups/scripts`

Generated 2026-07-04T08:24:18Z

AUC regressed at full-train: 0.9979 -> 0.9952

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9981)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `956e522f2c6a5ae2` | `34eee463147e0095` | `623a43cb64cbc641` |
| PR AUC | 0.9981 | 0.9936 | 0.9943 |
| ROC AUC | 0.9979 | 0.9946 | 0.9952 |
| F1 | 0.9787 | 0.9523 | 0.9569 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9979 -> 0.9952
