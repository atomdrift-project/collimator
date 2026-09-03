# Promote REJECTED — `33ae1bf11394fe2c` on `filegroups/portable`

Generated 2026-08-25T23:06:22Z

confirm did not hold: averaged ensemble PR_AUC regressed: 0.8834 -> 0.7911 (tol 0.0050, K=3)

## Gates

- **Confirm** (different seed, original profile): **FAIL** — averaged ensemble PR_AUC regressed: 0.8834 -> 0.7911 (tol 0.0050, K=3)
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `33ae1bf11394fe2c` | `c0236d3a203b37cc` | `—` |
| PR AUC | 0.8834 | 0.7911 | — |
| ROC AUC | 0.9432 | 0.9285 | — |
| F1 | 0.8336 | 0.8257 | — |

## Disposition

This spec did not survive the promotion ladder.

confirm did not hold: averaged ensemble PR_AUC regressed: 0.8834 -> 0.7911 (tol 0.0050, K=3)
