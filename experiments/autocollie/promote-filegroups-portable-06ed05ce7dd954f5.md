# Promote REJECTED — `06ed05ce7dd954f5` on `filegroups/portable`

Generated 2026-07-05T16:29:25Z

confirm did not hold: averaged ensemble PR_AUC regressed: 0.8541 -> 0.2130 (tol 0.0050, K=3)

## Gates

- **Confirm** (different seed, original profile): **FAIL** — averaged ensemble PR_AUC regressed: 0.8541 -> 0.2130 (tol 0.0050, K=3)
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `06ed05ce7dd954f5` | `99be126c900d30be` | `—` |
| PR AUC | 0.8541 | 0.2130 | — |
| ROC AUC | 0.9358 | 0.7255 | — |
| F1 | 0.8285 | 0.2634 | — |

## Disposition

This spec did not survive the promotion ladder.

confirm did not hold: averaged ensemble PR_AUC regressed: 0.8541 -> 0.2130 (tol 0.0050, K=3)
