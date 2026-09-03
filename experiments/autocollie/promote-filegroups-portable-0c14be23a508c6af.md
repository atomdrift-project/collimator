# Promote REJECTED — `0c14be23a508c6af` on `filegroups/portable`

Generated 2026-08-24T23:46:29Z

confirm did not hold: averaged ensemble PR_AUC regressed: 0.8769 -> 0.7929 (tol 0.0050, K=3)

## Gates

- **Confirm** (different seed, original profile): **FAIL** — averaged ensemble PR_AUC regressed: 0.8769 -> 0.7929 (tol 0.0050, K=3)
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `0c14be23a508c6af` | `68956494ad12a5c6` | `—` |
| PR AUC | 0.8769 | 0.7929 | — |
| ROC AUC | 0.9437 | 0.9345 | — |
| F1 | 0.8198 | 0.8318 | — |

## Disposition

This spec did not survive the promotion ladder.

confirm did not hold: averaged ensemble PR_AUC regressed: 0.8769 -> 0.7929 (tol 0.0050, K=3)
