# Promote REJECTED — `660e3f5ef1030b61` on `filetypes/powershell`

Generated 2026-05-20T16:12:39Z

AUC regressed at full-train: 0.9966 -> 0.9946

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9986)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `660e3f5ef1030b61` | `601bb9b46810cc13` | `b8e9ff84eeb5e69d` |
| PR AUC | 0.9986 | 0.9977 | 0.9977 |
| ROC AUC | 0.9966 | 0.9945 | 0.9946 |
| F1 | 0.9801 | 0.9822 | 0.9841 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9966 -> 0.9946
