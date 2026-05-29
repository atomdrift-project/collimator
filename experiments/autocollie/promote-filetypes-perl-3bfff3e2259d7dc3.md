# Promote REJECTED — `3bfff3e2259d7dc3` on `filetypes/perl`

Generated 2026-05-26T19:40:36Z

PR_AUC regressed at full-train: 1.0000 -> 0.9940

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `3bfff3e2259d7dc3` | `766b51b38748e5ef` | `3a72d43af1dc79e1` |
| PR AUC | 1.0000 | 0.9959 | 0.9940 |
| ROC AUC | 1.0000 | 0.9996 | 0.9994 |
| F1 | 0.9375 | 0.9756 | 0.9756 |

## Disposition

This spec did not survive the promotion ladder.

PR_AUC regressed at full-train: 1.0000 -> 0.9940
