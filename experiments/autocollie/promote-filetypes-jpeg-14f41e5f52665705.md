# Promote REJECTED — `14f41e5f52665705` on `filetypes/jpeg`

Generated 2026-06-03T16:15:30Z

AUC regressed at full-train: 0.9904 -> 0.9880

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9820)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `14f41e5f52665705` | `4f9574edcbf48f3a` | `9cd00e539251df7f` |
| PR AUC | 0.9820 | 0.9802 | 0.9773 |
| ROC AUC | 0.9904 | 0.9891 | 0.9880 |
| F1 | 0.8696 | 0.9268 | 0.9383 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9904 -> 0.9880
