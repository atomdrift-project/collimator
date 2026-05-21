# Promote REJECTED — `a73081138e09f95b` on `filetypes/perl`

Generated 2026-05-20T05:46:10Z

PR_AUC regressed at full-train: 0.9959 -> 0.9908

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9959)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `a73081138e09f95b` | `a2ee9ffbf67814b9` | `5a31ddb02649f47c` |
| PR AUC | 0.9959 | 0.9924 | 0.9908 |
| ROC AUC | 0.9996 | 0.9992 | 0.9989 |
| F1 | 0.8947 | 0.9130 | 0.9756 |

## Disposition

This spec did not survive the promotion ladder.

PR_AUC regressed at full-train: 0.9959 -> 0.9908
