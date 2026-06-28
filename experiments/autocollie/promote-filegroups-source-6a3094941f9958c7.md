# Promote REJECTED — `6a3094941f9958c7` on `filegroups/source`

Generated 2026-06-28T12:36:18Z

AUC regressed at full-train: 0.9982 -> 0.9966

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9990)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `6a3094941f9958c7` | `7a6605a340aef97f` | `024873580e8dd4d4` |
| PR AUC | 0.9990 | 0.9961 | 0.9962 |
| ROC AUC | 0.9982 | 0.9966 | 0.9966 |
| F1 | 0.9826 | 0.9714 | 0.9658 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9982 -> 0.9966
