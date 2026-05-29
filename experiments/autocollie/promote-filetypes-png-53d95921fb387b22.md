# Promote REJECTED — `53d95921fb387b22` on `filetypes/png`

Generated 2026-05-25T21:14:48Z

AUC regressed at full-train: 0.9692 -> 0.9648

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9838)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `53d95921fb387b22` | `ddbea59e76bf3375` | `c315c497d4b90cbd` |
| PR AUC | 0.9838 | 0.9820 | 0.9822 |
| ROC AUC | 0.9692 | 0.9630 | 0.9648 |
| F1 | 0.9268 | 0.9600 | 0.9600 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9692 -> 0.9648
