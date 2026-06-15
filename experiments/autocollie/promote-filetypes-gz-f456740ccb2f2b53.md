# Promote REJECTED — `f456740ccb2f2b53` on `filetypes/gz`

Generated 2026-06-14T23:39:45Z

AUC regressed at full-train: 0.8913 -> 0.8900

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.7218)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `f456740ccb2f2b53` | `156ee43e49129774` | `5063aee8d94fc2d5` |
| PR AUC | 0.7218 | 0.7228 | 0.7241 |
| ROC AUC | 0.8913 | 0.8774 | 0.8900 |
| F1 | 0.7899 | 0.8013 | 0.8004 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.8913 -> 0.8900
