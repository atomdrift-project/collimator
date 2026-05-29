# Promote REJECTED — `28aa3e107637d2b3` on `filetypes/shell`

Generated 2026-05-27T00:45:37Z

AUC regressed at full-train: 0.9995 -> 0.9983

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9984)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `28aa3e107637d2b3` | `a02d66568dc40ea1` | `d9b3d15e9d9a213b` |
| PR AUC | 0.9984 | 0.9974 | 0.9975 |
| ROC AUC | 0.9995 | 0.9982 | 0.9983 |
| F1 | 0.9756 | 0.9733 | 0.9687 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9995 -> 0.9983
