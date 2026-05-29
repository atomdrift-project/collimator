# Promote REJECTED — `803009e4a6d59070` on `filetypes/gz`

Generated 2026-05-26T20:52:40Z

AUC regressed at full-train: 1.0000 -> 0.9979

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `803009e4a6d59070` | `e622e9c3b2e47f2e` | `7568fbcc62b02198` |
| PR AUC | 1.0000 | 0.9985 | 0.9984 |
| ROC AUC | 1.0000 | 0.9980 | 0.9979 |
| F1 | 0.8000 | 0.9956 | 0.9956 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 1.0000 -> 0.9979
