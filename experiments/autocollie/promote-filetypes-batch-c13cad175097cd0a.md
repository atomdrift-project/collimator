# Promote REJECTED — `c13cad175097cd0a` on `filetypes/batch`

Generated 2026-05-26T22:27:54Z

AUC regressed at full-train: 0.9980 -> 0.9965

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9997)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `c13cad175097cd0a` | `eae9ed681fde7886` | `014d6aefae1061ba` |
| PR AUC | 0.9997 | 0.9995 | 0.9996 |
| ROC AUC | 0.9980 | 0.9960 | 0.9965 |
| F1 | 0.9863 | 0.9884 | 0.9884 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9980 -> 0.9965
