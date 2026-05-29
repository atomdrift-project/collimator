# Promote REJECTED — `3aff22984bbeb904` on `filetypes/batch`

Generated 2026-05-26T22:30:12Z

AUC regressed at full-train: 0.9977 -> 0.9964

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9997)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `3aff22984bbeb904` | `73ab6a3599199be2` | `8dcbfb537cf12245` |
| PR AUC | 0.9997 | 0.9996 | 0.9996 |
| ROC AUC | 0.9977 | 0.9963 | 0.9964 |
| F1 | 0.9917 | 0.9909 | 0.9922 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9977 -> 0.9964
