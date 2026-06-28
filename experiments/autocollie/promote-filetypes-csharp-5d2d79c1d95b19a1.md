# Promote REJECTED — `5d2d79c1d95b19a1` on `filetypes/csharp`

Generated 2026-06-28T11:00:43Z

AUC regressed at full-train: 0.9941 -> 0.9927

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9909)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `5d2d79c1d95b19a1` | `9146de50e4fb4dfc` | `bcf716c0bf3be4f9` |
| PR AUC | 0.9909 | 0.9874 | 0.9881 |
| ROC AUC | 0.9941 | 0.9922 | 0.9927 |
| F1 | 0.9431 | 0.9516 | 0.9551 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9941 -> 0.9927
