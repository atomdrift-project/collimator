# Promote REJECTED — `4defc3ac4afacdb9` on `filetypes/batch`

Generated 2026-07-04T13:51:08Z

AUC regressed at full-train: 0.9294 -> 0.9043

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9895)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `4defc3ac4afacdb9` | `f20d203d5a81883c` | `1aadfbce6b00f38b` |
| PR AUC | 0.9895 | 0.9926 | 0.9936 |
| ROC AUC | 0.9294 | 0.8985 | 0.9043 |
| F1 | 0.2978 | 0.9947 | 0.9962 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9294 -> 0.9043
