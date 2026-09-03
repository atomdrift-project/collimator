# Promote REJECTED — `2a6ec5421a20c17e` on `filetypes/batch`

Generated 2026-08-25T00:01:08Z

AUC regressed at full-train: 0.9929 -> 0.9848

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9990)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `2a6ec5421a20c17e` | `e23ce042d20a421a` | `7081357fb7762907` |
| PR AUC | 0.9990 | 0.9996 | 0.9990 |
| ROC AUC | 0.9929 | 0.9928 | 0.9848 |
| F1 | 0.2947 | 0.9971 | 0.9969 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9929 -> 0.9848
