# Promote REJECTED — `869759a839b13ed6` on `filetypes/rust`

Generated 2026-05-27T05:10:49Z

PR_AUC regressed at full-train: 0.9006 -> 0.8809

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9006)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `869759a839b13ed6` | `b09bb4f04b61591a` | `e455071270eea8fe` |
| PR AUC | 0.9006 | 0.9280 | 0.8809 |
| ROC AUC | 0.9862 | 0.9902 | 0.9881 |
| F1 | 0.6957 | 0.7879 | 0.8387 |

## Disposition

This spec did not survive the promotion ladder.

PR_AUC regressed at full-train: 0.9006 -> 0.8809
