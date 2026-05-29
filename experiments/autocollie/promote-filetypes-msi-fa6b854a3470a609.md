# Promote REJECTED — `fa6b854a3470a609` on `filetypes/msi`

Generated 2026-05-26T22:00:12Z

AUC regressed at full-train: 0.9990 -> 0.9963

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9999)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `fa6b854a3470a609` | `2eadbf9655aa6ade` | `c676f6f8363d5352` |
| PR AUC | 0.9999 | 0.9997 | 0.9999 |
| ROC AUC | 0.9990 | 0.9903 | 0.9963 |
| F1 | 0.9928 | 0.9950 | 0.9967 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9990 -> 0.9963
