# Promote REJECTED — `0b784ab9ed7c2000` on `filegroups/portable`

Generated 2026-08-04T23:55:32Z

confirm did not hold: averaged ensemble PR_AUC regressed: 0.8725 -> 0.7925 (tol 0.0050, K=3)

## Gates

- **Confirm** (different seed, original profile): **FAIL** — averaged ensemble PR_AUC regressed: 0.8725 -> 0.7925 (tol 0.0050, K=3)
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `0b784ab9ed7c2000` | `0cefed44bc723903` | `—` |
| PR AUC | 0.8725 | 0.7925 | — |
| ROC AUC | 0.9168 | 0.9367 | — |
| F1 | 0.8269 | 0.8268 | — |

## Disposition

This spec did not survive the promotion ladder.

confirm did not hold: averaged ensemble PR_AUC regressed: 0.8725 -> 0.7925 (tol 0.0050, K=3)
