# Promote REJECTED — `b38aff58277abb5d` on `filetypes/csharp`

Generated 2026-06-09T09:57:48Z

AUC regressed at full-train: 0.9950 -> 0.9939

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9930)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `b38aff58277abb5d` | `a0fc7d9b02c0196e` | `21eb94252d01fbd3` |
| PR AUC | 0.9930 | 0.9911 | 0.9914 |
| ROC AUC | 0.9950 | 0.9934 | 0.9939 |
| F1 | 0.9557 | 0.9662 | 0.9662 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9950 -> 0.9939
