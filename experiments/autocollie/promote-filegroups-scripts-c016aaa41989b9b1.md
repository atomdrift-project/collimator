# Promote REJECTED — `c016aaa41989b9b1` on `filegroups/scripts`

Generated 2026-08-25T23:16:45Z

confirm did not hold: averaged ensemble PR_AUC regressed: 0.9872 -> 0.9434 (tol 0.0050, K=3)

## Gates

- **Confirm** (different seed, original profile): **FAIL** — averaged ensemble PR_AUC regressed: 0.9872 -> 0.9434 (tol 0.0050, K=3)
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `c016aaa41989b9b1` | `141670fd030518e9` | `—` |
| PR AUC | 0.9872 | 0.9434 | — |
| ROC AUC | 0.9851 | 0.9894 | — |
| F1 | 0.7095 | 0.9310 | — |

## Disposition

This spec did not survive the promotion ladder.

confirm did not hold: averaged ensemble PR_AUC regressed: 0.9872 -> 0.9434 (tol 0.0050, K=3)
