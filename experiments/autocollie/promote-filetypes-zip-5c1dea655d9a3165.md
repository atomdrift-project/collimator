# Promote REJECTED — `5c1dea655d9a3165` on `filetypes/zip`

Generated 2026-05-26T23:15:21Z

AUC regressed at full-train: 0.9983 -> 0.9965

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9999)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `5c1dea655d9a3165` | `9d298c7e1afe8506` | `418b830b6b2843ad` |
| PR AUC | 0.9999 | 0.9998 | 0.9998 |
| ROC AUC | 0.9983 | 0.9963 | 0.9965 |
| F1 | 0.0000 | 0.8091 | 0.8043 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9983 -> 0.9965
