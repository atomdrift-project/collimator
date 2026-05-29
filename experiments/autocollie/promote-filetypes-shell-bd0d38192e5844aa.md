# Promote REJECTED — `bd0d38192e5844aa` on `filetypes/shell`

Generated 2026-05-27T00:45:17Z

AUC regressed at full-train: 0.9995 -> 0.9983

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9984)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `bd0d38192e5844aa` | `2a83accac78675ab` | `ecf079b648b75083` |
| PR AUC | 0.9984 | 0.9974 | 0.9975 |
| ROC AUC | 0.9995 | 0.9982 | 0.9983 |
| F1 | 0.9756 | 0.9733 | 0.9687 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9995 -> 0.9983
