# Promote REJECTED — `825216f29184cdc5` on `filetypes/text`

Generated 2026-05-27T01:52:39Z

PR_AUC regressed at full-train: 0.9703 -> 0.9649

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9703)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `825216f29184cdc5` | `4ffea8c2e1af9c57` | `c83352c31f077655` |
| PR AUC | 0.9703 | 0.9735 | 0.9649 |
| ROC AUC | 0.9851 | 0.9881 | 0.9826 |
| F1 | 0.8333 | 0.9130 | 0.8571 |

## Disposition

This spec did not survive the promotion ladder.

PR_AUC regressed at full-train: 0.9703 -> 0.9649
