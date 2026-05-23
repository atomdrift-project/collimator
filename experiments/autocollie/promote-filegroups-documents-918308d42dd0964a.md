# Promote REJECTED — `918308d42dd0964a` on `filegroups/documents`

Generated 2026-05-23T17:25:43Z

AUC regressed at full-train: 0.9987 -> 0.9879

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `918308d42dd0964a` | `f6fc01da1e63b1d0` | `159bcd16eef2f1d5` |
| PR AUC | 1.0000 | 0.9986 | 0.9999 |
| ROC AUC | 0.9987 | 0.8989 | 0.9879 |
| F1 | 0.9974 | 0.9965 | 0.9965 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9987 -> 0.9879
