# Promote REJECTED — `ef3a699babcc85d4` on `filegroups/scripts`

Generated 2026-08-05T00:54:57Z

confirm did not hold: averaged ensemble PR_AUC regressed: 0.9876 -> 0.9652 (tol 0.0050, K=3)

## Gates

- **Confirm** (different seed, original profile): **FAIL** — averaged ensemble PR_AUC regressed: 0.9876 -> 0.9652 (tol 0.0050, K=3)
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `ef3a699babcc85d4` | `57e4c88436bd8d16` | `—` |
| PR AUC | 0.9876 | 0.9652 | — |
| ROC AUC | 0.9855 | 0.9904 | — |
| F1 | 0.7042 | 0.9528 | — |

## Disposition

This spec did not survive the promotion ladder.

confirm did not hold: averaged ensemble PR_AUC regressed: 0.9876 -> 0.9652 (tol 0.0050, K=3)
