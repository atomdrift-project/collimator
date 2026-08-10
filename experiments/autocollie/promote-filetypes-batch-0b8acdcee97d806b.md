# Promote REJECTED — `0b8acdcee97d806b` on `filetypes/batch`

Generated 2026-08-04T21:10:08Z

AUC regressed at full-train: 0.9868 -> 0.9847

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9982)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `0b8acdcee97d806b` | `f3001f006573adf1` | `244dbdfaf5038de0` |
| PR AUC | 0.9982 | 0.9990 | 0.9989 |
| ROC AUC | 0.9868 | 0.9863 | 0.9847 |
| F1 | 0.9938 | 0.9978 | 0.9977 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9868 -> 0.9847
