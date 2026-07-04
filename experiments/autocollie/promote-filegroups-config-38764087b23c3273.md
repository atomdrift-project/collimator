# Promote REJECTED — `38764087b23c3273` on `filegroups/config`

Generated 2026-07-04T12:51:23Z

AUC regressed at full-train: 0.9995 -> 0.9979

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9997)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `38764087b23c3273` | `864d1b0e38c364a9` | `2c61e8b88821c1d2` |
| PR AUC | 0.9997 | 0.9981 | 0.9979 |
| ROC AUC | 0.9995 | 0.9981 | 0.9979 |
| F1 | 0.9954 | 0.9848 | 0.9854 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9995 -> 0.9979
