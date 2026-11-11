# Promote REJECTED — `d456947b6e34433b` on `filetypes/go`

Generated 2026-11-10T19:53:04Z

PR_AUC regressed at full-train: 0.9316 -> 0.9084

## Gates

- **Confirm** (different seed, original profile): **PASS** — averaged 3-seed ensemble PR_AUC held: 0.9316 -> 0.9413; individual seeds may be noisy
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `d456947b6e34433b` | `95c551f107a3c971` | `3325d0308703d185` |
| PR AUC | 0.9316 | 0.9413 | 0.9084 |
| ROC AUC | 0.9742 | 0.9810 | 0.9817 |
| F1 | 0.8893 | 0.9053 | 0.8726 |

## Disposition

This spec did not survive the promotion ladder.

PR_AUC regressed at full-train: 0.9316 -> 0.9084
