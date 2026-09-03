# Promote REJECTED — `2abc6a0b3e208848` on `filegroups/scripts`

Generated 2026-08-25T00:00:37Z

confirm did not hold: averaged ensemble PR_AUC regressed: 0.9878 -> 0.9455 (tol 0.0050, K=3)

## Gates

- **Confirm** (different seed, original profile): **FAIL** — averaged ensemble PR_AUC regressed: 0.9878 -> 0.9455 (tol 0.0050, K=3)
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `2abc6a0b3e208848` | `c919c1c9caf5543a` | `—` |
| PR AUC | 0.9878 | 0.9455 | — |
| ROC AUC | 0.9856 | 0.9893 | — |
| F1 | 0.7171 | 0.9334 | — |

## Disposition

This spec did not survive the promotion ladder.

confirm did not hold: averaged ensemble PR_AUC regressed: 0.9878 -> 0.9455 (tol 0.0050, K=3)
