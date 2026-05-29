# Promote REJECTED — `97c9b5c13655ee66` on `filetypes/batch`

Generated 2026-05-26T22:28:23Z

AUC regressed at full-train: 0.9980 -> 0.9965

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9998)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `97c9b5c13655ee66` | `d71092d7d2361102` | `caad17583ccf385d` |
| PR AUC | 0.9998 | 0.9996 | 0.9996 |
| ROC AUC | 0.9980 | 0.9968 | 0.9965 |
| F1 | 0.9904 | 0.9909 | 0.9909 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9980 -> 0.9965
