# Promote REJECTED — `739734f5cba4b62c` on `filegroups/media`

Generated 2026-07-03T04:31:02Z

confirm did not hold: averaged ensemble PR_AUC regressed: 0.3443 -> 0.1111 (tol 0.0050, K=3)

## Gates

- **Confirm** (different seed, original profile): **FAIL** — averaged ensemble PR_AUC regressed: 0.3443 -> 0.1111 (tol 0.0050, K=3)
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `739734f5cba4b62c` | `8fa7e2fc33ca9f65` | `—` |
| PR AUC | 0.3443 | 0.1111 | — |
| ROC AUC | 0.7566 | 0.4280 | — |
| F1 | 0.1567 | 0.1298 | — |

## Disposition

This spec did not survive the promotion ladder.

confirm did not hold: averaged ensemble PR_AUC regressed: 0.3443 -> 0.1111 (tol 0.0050, K=3)
