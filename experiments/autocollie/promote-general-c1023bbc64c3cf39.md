# Promote REJECTED — `c1023bbc64c3cf39` on `general`

Generated 2026-06-08T16:10:25Z

confirm did not hold: averaged ensemble PR_AUC regressed: 0.9757 -> 0.9532 (tol 0.0050, K=3)

## Gates

- **Confirm** (different seed, original profile): **FAIL** — averaged ensemble PR_AUC regressed: 0.9757 -> 0.9532 (tol 0.0050, K=3)
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `c1023bbc64c3cf39` | `a5f205d4f99c8b82` | `—` |
| PR AUC | 0.9757 | 0.9532 | — |
| ROC AUC | 0.9706 | 0.9621 | — |
| F1 | 0.9057 | 0.8341 | — |

## Disposition

This spec did not survive the promotion ladder.

confirm did not hold: averaged ensemble PR_AUC regressed: 0.9757 -> 0.9532 (tol 0.0050, K=3)
