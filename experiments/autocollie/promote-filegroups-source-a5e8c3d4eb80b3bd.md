# Promote REJECTED — `a5e8c3d4eb80b3bd` on `filegroups/source`

Generated 2026-08-25T00:04:38Z

confirm did not hold: averaged ensemble PR_AUC regressed: 0.9379 -> 0.6704 (tol 0.0050, K=3)

## Gates

- **Confirm** (different seed, original profile): **FAIL** — averaged ensemble PR_AUC regressed: 0.9379 -> 0.6704 (tol 0.0050, K=3)
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `a5e8c3d4eb80b3bd` | `8dae835fd46ed82d` | `—` |
| PR AUC | 0.9379 | 0.6704 | — |
| ROC AUC | 0.9288 | 0.9328 | — |
| F1 | 0.7098 | 0.6755 | — |

## Disposition

This spec did not survive the promotion ladder.

confirm did not hold: averaged ensemble PR_AUC regressed: 0.9379 -> 0.6704 (tol 0.0050, K=3)
