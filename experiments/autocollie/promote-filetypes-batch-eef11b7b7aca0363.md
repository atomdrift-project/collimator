# Promote REJECTED — `eef11b7b7aca0363` on `filetypes/batch`

Generated 2026-05-25T20:28:58Z

AUC regressed at full-train: 0.9983 -> 0.9965

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9998)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `eef11b7b7aca0363` | `b2ce54256769e342` | `175dbdfd826e3fff` |
| PR AUC | 0.9998 | 0.9995 | 0.9996 |
| ROC AUC | 0.9983 | 0.9960 | 0.9965 |
| F1 | 0.9890 | 0.9884 | 0.9884 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9983 -> 0.9965
