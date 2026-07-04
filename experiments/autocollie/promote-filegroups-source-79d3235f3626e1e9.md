# Promote REJECTED — `79d3235f3626e1e9` on `filegroups/source`

Generated 2026-07-04T15:46:23Z

confirm did not hold: averaged ensemble PR_AUC regressed: 0.8672 -> 0.4638 (tol 0.0050, K=3)

## Gates

- **Confirm** (different seed, original profile): **FAIL** — averaged ensemble PR_AUC regressed: 0.8672 -> 0.4638 (tol 0.0050, K=3)
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `79d3235f3626e1e9` | `d798045f3f018ea9` | `—` |
| PR AUC | 0.8672 | 0.4638 | — |
| ROC AUC | 0.8472 | 0.8441 | — |
| F1 | 0.5595 | 0.2891 | — |

## Disposition

This spec did not survive the promotion ladder.

confirm did not hold: averaged ensemble PR_AUC regressed: 0.8672 -> 0.4638 (tol 0.0050, K=3)
