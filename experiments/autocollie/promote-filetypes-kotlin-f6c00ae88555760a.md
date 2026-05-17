# Promote REJECTED — `f6c00ae88555760a` on `filetypes/kotlin`

Generated 2026-05-15T00:31:03Z

AUC regressed at full-train: 0.9994 -> 0.9956

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `f6c00ae88555760a` | `2cf44129e4c6756d` | `702c6e2b84541626` |
| PR AUC | 1.0000 | 1.0000 | 0.9999 |
| ROC AUC | 0.9994 | 0.9984 | 0.9956 |
| F1 | 0.9982 | 0.9982 | 0.9969 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9994 -> 0.9956
