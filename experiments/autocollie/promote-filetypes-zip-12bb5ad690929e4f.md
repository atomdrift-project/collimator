# Promote REJECTED — `12bb5ad690929e4f` on `filetypes/zip`

Generated 2026-05-26T23:48:04Z

AUC regressed at full-train: 0.9976 -> 0.9952

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9999)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `12bb5ad690929e4f` | `6479be22ad76e90d` | `60595ac4e36f08c5` |
| PR AUC | 0.9999 | 0.9998 | 0.9997 |
| ROC AUC | 0.9976 | 0.9958 | 0.9952 |
| F1 | 0.9760 | 0.9948 | 0.9948 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9976 -> 0.9952
