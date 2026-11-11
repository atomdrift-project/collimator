# Promote REJECTED — `c45a9d762fc22bac` on `filetypes/chrome_manifest`

Generated 2026-11-06T01:21:05Z

confirm did not hold: averaged ensemble PR_AUC regressed: 0.9889 -> 0.9798 (tol 0.0050, K=3)

## Gates

- **Confirm** (different seed, original profile): **FAIL** — averaged ensemble PR_AUC regressed: 0.9889 -> 0.9798 (tol 0.0050, K=3)
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `c45a9d762fc22bac` | `883d0a55039a3307` | `—` |
| PR AUC | 0.9889 | 0.9798 | — |
| ROC AUC | 0.9992 | 0.9983 | — |
| F1 | 0.9474 | 0.9412 | — |

## Disposition

This spec did not survive the promotion ladder.

confirm did not hold: averaged ensemble PR_AUC regressed: 0.9889 -> 0.9798 (tol 0.0050, K=3)
