# Promote REJECTED — `7a70f0c368c9a0ea` on `filetypes/batch`

Generated 2026-08-05T14:56:30Z

AUC regressed at full-train: 0.9928 -> 0.9757

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9990)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `7a70f0c368c9a0ea` | `da5fa11b26015642` | `700da9f3869d60ee` |
| PR AUC | 0.9990 | 0.9985 | 0.9981 |
| ROC AUC | 0.9928 | 0.9797 | 0.9757 |
| F1 | 0.2983 | 0.9975 | 0.9976 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9928 -> 0.9757
