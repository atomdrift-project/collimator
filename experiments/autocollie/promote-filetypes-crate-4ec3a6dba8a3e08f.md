# Promote REJECTED — `4ec3a6dba8a3e08f` on `filetypes/crate`

Generated 2026-11-06T01:51:12Z

confirm did not hold: averaged ensemble PR_AUC regressed: 0.9341 -> 0.1030 (tol 0.0050, K=3)

## Gates

- **Confirm** (different seed, original profile): **FAIL** — averaged ensemble PR_AUC regressed: 0.9341 -> 0.1030 (tol 0.0050, K=3)
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `4ec3a6dba8a3e08f` | `f15413ef90bacf2e` | `—` |
| PR AUC | 0.9341 | 0.1030 | — |
| ROC AUC | 0.9999 | 0.9013 | — |
| F1 | 0.2500 | 0.2105 | — |

## Disposition

This spec did not survive the promotion ladder.

confirm did not hold: averaged ensemble PR_AUC regressed: 0.9341 -> 0.1030 (tol 0.0050, K=3)
