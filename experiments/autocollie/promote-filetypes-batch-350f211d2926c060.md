# Promote REJECTED — `350f211d2926c060` on `filetypes/batch`

Generated 2026-05-26T22:28:08Z

AUC regressed at full-train: 0.9980 -> 0.9965

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9998)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `350f211d2926c060` | `46e1119dd0f9ff90` | `187998a535d44311` |
| PR AUC | 0.9998 | 0.9996 | 0.9996 |
| ROC AUC | 0.9980 | 0.9968 | 0.9965 |
| F1 | 0.9904 | 0.9909 | 0.9909 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9980 -> 0.9965
