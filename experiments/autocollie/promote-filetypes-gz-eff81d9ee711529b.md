# Promote REJECTED — `eff81d9ee711529b` on `filetypes/gz`

Generated 2026-05-25T20:14:03Z

AUC regressed at full-train: 1.0000 -> 0.9982

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `eff81d9ee711529b` | `e622e9c3b2e47f2e` | `47ff785ebfd2ceaf` |
| PR AUC | 1.0000 | 0.9985 | 0.9986 |
| ROC AUC | 1.0000 | 0.9980 | 0.9982 |
| F1 | 0.8750 | 0.9956 | 0.9956 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 1.0000 -> 0.9982
