# Promote REJECTED — `2673dc12b5d52386` on `filegroups/portable`

Generated 2026-08-27T10:02:11Z

confirm did not hold: averaged ensemble PR_AUC regressed: 0.8502 -> 0.7918 (tol 0.0050, K=3)

## Gates

- **Confirm** (different seed, original profile): **FAIL** — averaged ensemble PR_AUC regressed: 0.8502 -> 0.7918 (tol 0.0050, K=3)
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `2673dc12b5d52386` | `22b4c2ed152b86f4` | `—` |
| PR AUC | 0.8502 | 0.7918 | — |
| ROC AUC | 0.9091 | 0.9152 | — |
| F1 | 0.8317 | 0.8317 | — |

## Disposition

This spec did not survive the promotion ladder.

confirm did not hold: averaged ensemble PR_AUC regressed: 0.8502 -> 0.7918 (tol 0.0050, K=3)
