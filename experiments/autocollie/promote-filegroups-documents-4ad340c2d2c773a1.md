# Promote REJECTED — `4ad340c2d2c773a1` on `filegroups/documents`

Generated 2026-06-14T20:10:27Z

AUC regressed at full-train: 0.9997 -> 0.9982

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `4ad340c2d2c773a1` | `70cbaef6b64f72cb` | `1416458a03aae236` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9997 | 0.9982 | 0.9982 |
| F1 | 0.9868 | 0.9587 | 0.9589 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9997 -> 0.9982
