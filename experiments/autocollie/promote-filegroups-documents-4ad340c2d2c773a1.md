# Promote REJECTED — `4ad340c2d2c773a1` on `filegroups/documents`

Generated 2026-07-04T08:09:56Z

AUC regressed at full-train: 0.9997 -> 0.9966

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `4ad340c2d2c773a1` | `f60d00cc0ede4315` | `391d77cc5f1847cf` |
| PR AUC | 1.0000 | 0.9999 | 0.9999 |
| ROC AUC | 0.9997 | 0.9965 | 0.9966 |
| F1 | 0.9868 | 0.9434 | 0.9415 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9997 -> 0.9966
