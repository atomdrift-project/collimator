# Promote REJECTED — `c04b95b498e7221e` on `filetypes/python`

Generated 2026-06-08T18:27:28Z

AUC regressed at full-train: 0.9989 -> 0.9952

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9989)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `c04b95b498e7221e` | `ea8d3dbab56212cb` | `da82bab8e633f455` |
| PR AUC | 0.9989 | 0.9941 | 0.9943 |
| ROC AUC | 0.9989 | 0.9950 | 0.9952 |
| F1 | 0.9825 | 0.9558 | 0.9639 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9989 -> 0.9952
