# Promote REJECTED — `9165276b845f9226` on `filegroups/source`

Generated 2026-07-05T18:31:39Z

confirm did not hold: averaged ensemble PR_AUC regressed: 0.8644 -> 0.5262 (tol 0.0050, K=3)

## Gates

- **Confirm** (different seed, original profile): **FAIL** — averaged ensemble PR_AUC regressed: 0.8644 -> 0.5262 (tol 0.0050, K=3)
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `9165276b845f9226` | `1539b23c1c278395` | `—` |
| PR AUC | 0.8644 | 0.5262 | — |
| ROC AUC | 0.8468 | 0.8817 | — |
| F1 | 0.5234 | 0.4475 | — |

## Disposition

This spec did not survive the promotion ladder.

confirm did not hold: averaged ensemble PR_AUC regressed: 0.8644 -> 0.5262 (tol 0.0050, K=3)
