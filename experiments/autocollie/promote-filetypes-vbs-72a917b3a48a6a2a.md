# Promote REJECTED — `72a917b3a48a6a2a` on `filetypes/vbs`

Generated 2026-06-14T04:49:41Z

AUC regressed at full-train: 0.9926 -> 0.9901

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9978)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `72a917b3a48a6a2a` | `f10ff0c8eccbcb59` | `f6c1e7a161dd4999` |
| PR AUC | 0.9978 | 0.9975 | 0.9973 |
| ROC AUC | 0.9926 | 0.9909 | 0.9901 |
| F1 | 0.9593 | 0.9758 | 0.9761 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9926 -> 0.9901
