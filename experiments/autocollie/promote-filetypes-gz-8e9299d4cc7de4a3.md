# Promote REJECTED — `8e9299d4cc7de4a3` on `filetypes/gz`

Generated 2026-05-26T20:53:16Z

AUC regressed at full-train: 1.0000 -> 0.9980

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `8e9299d4cc7de4a3` | `c6f07eff70a29223` | `6802ed7846fee4a3` |
| PR AUC | 1.0000 | 0.9986 | 0.9985 |
| ROC AUC | 1.0000 | 0.9981 | 0.9980 |
| F1 | 0.6154 | 0.9956 | 0.9956 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 1.0000 -> 0.9980
