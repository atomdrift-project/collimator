# Promote REJECTED — `4f7debde1c13d38e` on `filetypes/pdf`

Generated 2026-07-05T17:48:35Z

AUC regressed at full-train: 0.9742 -> 0.9580

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9910)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `4f7debde1c13d38e` | `e4450e1c657e7d0e` | `9773096a4885af93` |
| PR AUC | 0.9910 | 0.9932 | 0.9932 |
| ROC AUC | 0.9742 | 0.9582 | 0.9580 |
| F1 | 0.8528 | 0.9719 | 0.9737 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9742 -> 0.9580
