# Promote REJECTED — `e77c6bd1c31c65ea` on `filetypes/text`

Generated 2026-05-19T20:49:49Z

AUC regressed at full-train: 0.9764 -> 0.9747

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9564)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `e77c6bd1c31c65ea` | `2e3438bc669b3ab2` | `3f54855119c5e983` |
| PR AUC | 0.9564 | 0.9532 | 0.9517 |
| ROC AUC | 0.9764 | 0.9755 | 0.9747 |
| F1 | 0.8444 | 0.8462 | 0.8302 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9764 -> 0.9747
