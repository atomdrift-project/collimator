# Promote REJECTED — `97d28d988e99a59b` on `filetypes/batch`

Generated 2026-05-26T22:28:37Z

AUC regressed at full-train: 0.9983 -> 0.9957

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9998)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `97d28d988e99a59b` | `16974a6869afdd53` | `65e995fdbf0e83de` |
| PR AUC | 0.9998 | 0.9995 | 0.9995 |
| ROC AUC | 0.9983 | 0.9959 | 0.9957 |
| F1 | 0.9850 | 0.9845 | 0.9845 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9983 -> 0.9957
