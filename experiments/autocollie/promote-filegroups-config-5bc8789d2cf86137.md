# Promote REJECTED — `5bc8789d2cf86137` on `filegroups/config`

Generated 2026-07-04T13:52:04Z

confirm did not hold: averaged ensemble PR_AUC regressed: 0.9019 -> 0.8258 (tol 0.0050, K=3)

## Gates

- **Confirm** (different seed, original profile): **FAIL** — averaged ensemble PR_AUC regressed: 0.9019 -> 0.8258 (tol 0.0050, K=3)
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `5bc8789d2cf86137` | `91ca8299fbb1e7f0` | `—` |
| PR AUC | 0.9019 | 0.8258 | — |
| ROC AUC | 0.9290 | 0.9143 | — |
| F1 | 0.8690 | 0.8747 | — |

## Disposition

This spec did not survive the promotion ladder.

confirm did not hold: averaged ensemble PR_AUC regressed: 0.9019 -> 0.8258 (tol 0.0050, K=3)
