# Promote REJECTED — `6877a11337231b0c` on `filetypes/msi`

Generated 2026-05-26T21:51:24Z

AUC regressed at full-train: 1.0000 -> 0.9963

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `6877a11337231b0c` | `5a5431a83331087a` | `9ecebfafc668b5f3` |
| PR AUC | 1.0000 | 0.9999 | 0.9999 |
| ROC AUC | 1.0000 | 0.9970 | 0.9963 |
| F1 | 0.9818 | 0.9967 | 0.9967 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 1.0000 -> 0.9963
