# Promote REJECTED — `bcbadf3afbe9bd0b` on `filetypes/java`

Generated 2026-07-23T05:05:40Z

confirm did not hold: averaged ensemble PR_AUC regressed: 0.9583 -> 0.9461 (tol 0.0050, K=3)

## Gates

- **Confirm** (different seed, original profile): **FAIL** — averaged ensemble PR_AUC regressed: 0.9583 -> 0.9461 (tol 0.0050, K=3)
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `bcbadf3afbe9bd0b` | `214f3491217bfa3d` | `—` |
| PR AUC | 0.9583 | 0.9461 | — |
| ROC AUC | 0.9951 | 0.9931 | — |
| F1 | 0.8980 | 0.9072 | — |

## Disposition

This spec did not survive the promotion ladder.

confirm did not hold: averaged ensemble PR_AUC regressed: 0.9583 -> 0.9461 (tol 0.0050, K=3)
