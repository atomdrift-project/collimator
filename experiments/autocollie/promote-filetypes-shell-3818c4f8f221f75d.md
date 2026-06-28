# Promote REJECTED — `3818c4f8f221f75d` on `filetypes/shell`

Generated 2026-06-28T13:04:17Z

AUC regressed at full-train: 0.9976 -> 0.9956

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9963)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `3818c4f8f221f75d` | `5fab59648f0cc4c3` | `df2d13bfa223ace8` |
| PR AUC | 0.9963 | 0.9943 | 0.9944 |
| ROC AUC | 0.9976 | 0.9956 | 0.9956 |
| F1 | 0.9650 | 0.9645 | 0.9598 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9976 -> 0.9956
