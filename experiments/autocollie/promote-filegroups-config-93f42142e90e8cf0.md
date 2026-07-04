# Promote REJECTED — `93f42142e90e8cf0` on `filegroups/config`

Generated 2026-07-04T12:52:28Z

AUC regressed at full-train: 0.9996 -> 0.9979

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9998)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `93f42142e90e8cf0` | `73b9344f5857c159` | `164b9c329462f01f` |
| PR AUC | 0.9998 | 0.9980 | 0.9980 |
| ROC AUC | 0.9996 | 0.9980 | 0.9979 |
| F1 | 0.9939 | 0.9869 | 0.9891 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9996 -> 0.9979
