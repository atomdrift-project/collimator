# Promote REJECTED — `1b8083fa32ece294` on `filegroups/source`

Generated 2026-07-03T03:01:29Z

confirm did not hold: averaged ensemble PR_AUC regressed: 0.8717 -> 0.5378 (tol 0.0050, K=3)

## Gates

- **Confirm** (different seed, original profile): **FAIL** — averaged ensemble PR_AUC regressed: 0.8717 -> 0.5378 (tol 0.0050, K=3)
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `1b8083fa32ece294` | `ad8049cc8e521376` | `—` |
| PR AUC | 0.8717 | 0.5378 | — |
| ROC AUC | 0.8515 | 0.8919 | — |
| F1 | 0.5719 | 0.4555 | — |

## Disposition

This spec did not survive the promotion ladder.

confirm did not hold: averaged ensemble PR_AUC regressed: 0.8717 -> 0.5378 (tol 0.0050, K=3)
