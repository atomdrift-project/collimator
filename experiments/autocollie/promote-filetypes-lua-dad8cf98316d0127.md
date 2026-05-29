# Promote REJECTED — `dad8cf98316d0127` on `filetypes/lua`

Generated 2026-05-27T05:24:58Z

PR_AUC regressed at full-train: 0.6738 -> 0.6562

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.6738)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `dad8cf98316d0127` | `97490397a42ee18e` | `03f273314f8397d9` |
| PR AUC | 0.6738 | 0.7431 | 0.6562 |
| ROC AUC | 0.8370 | 0.8478 | 0.8152 |
| F1 | 0.4000 | 0.7500 | 0.5000 |

## Disposition

This spec did not survive the promotion ladder.

PR_AUC regressed at full-train: 0.6738 -> 0.6562
