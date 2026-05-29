# Promote REJECTED — `e120c1c93a738dc1` on `filetypes/gz`

Generated 2026-05-26T20:52:46Z

AUC regressed at full-train: 1.0000 -> 0.9977

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `e120c1c93a738dc1` | `aac33f62a9731d79` | `736badce3cf067cb` |
| PR AUC | 1.0000 | 0.9982 | 0.9983 |
| ROC AUC | 1.0000 | 0.9975 | 0.9977 |
| F1 | 0.5000 | 0.9913 | 0.9913 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 1.0000 -> 0.9977
