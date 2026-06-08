# Promote REJECTED — `859d578ae91ea04d` on `filegroups/source`

Generated 2026-06-08T16:10:26Z

confirm did not hold: averaged ensemble PR_AUC regressed: 0.9051 -> 0.6478 (tol 0.0050, K=3)

## Gates

- **Confirm** (different seed, original profile): **FAIL** — averaged ensemble PR_AUC regressed: 0.9051 -> 0.6478 (tol 0.0050, K=3)
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `859d578ae91ea04d` | `aaa3d9d0dba741c9` | `—` |
| PR AUC | 0.9051 | 0.6478 | — |
| ROC AUC | 0.9126 | 0.9214 | — |
| F1 | 0.5554 | 0.5632 | — |

## Disposition

This spec did not survive the promotion ladder.

confirm did not hold: averaged ensemble PR_AUC regressed: 0.9051 -> 0.6478 (tol 0.0050, K=3)
