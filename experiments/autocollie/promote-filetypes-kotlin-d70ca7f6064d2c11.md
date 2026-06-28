# Promote REJECTED — `d70ca7f6064d2c11` on `filetypes/kotlin`

Generated 2026-06-28T11:35:37Z

AUC regressed at full-train: 0.9949 -> 0.9917

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9999)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `d70ca7f6064d2c11` | `cf5ff714a1449257` | `e72af17ef6d054a6` |
| PR AUC | 0.9999 | 0.9997 | 0.9998 |
| ROC AUC | 0.9949 | 0.9887 | 0.9917 |
| F1 | 0.9971 | 0.9965 | 0.9973 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9949 -> 0.9917
