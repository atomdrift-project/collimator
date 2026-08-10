# Promote REJECTED — `ee9d8950d4c567e9` on `filegroups/source`

Generated 2026-08-05T00:39:25Z

confirm did not hold: averaged ensemble PR_AUC regressed: 0.9337 -> 0.6715 (tol 0.0050, K=3)

## Gates

- **Confirm** (different seed, original profile): **FAIL** — averaged ensemble PR_AUC regressed: 0.9337 -> 0.6715 (tol 0.0050, K=3)
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `ee9d8950d4c567e9` | `18a51bcc6090a546` | `—` |
| PR AUC | 0.9337 | 0.6715 | — |
| ROC AUC | 0.9210 | 0.9271 | — |
| F1 | 0.7297 | 0.6752 | — |

## Disposition

This spec did not survive the promotion ladder.

confirm did not hold: averaged ensemble PR_AUC regressed: 0.9337 -> 0.6715 (tol 0.0050, K=3)
