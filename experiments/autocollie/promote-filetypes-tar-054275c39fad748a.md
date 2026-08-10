# Promote REJECTED — `054275c39fad748a` on `filetypes/tar`

Generated 2026-08-05T14:57:40Z

AUC regressed at full-train: 0.9655 -> 0.9619

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9380)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `054275c39fad748a` | `022c927fcaca5b74` | `d76e55dfe045e860` |
| PR AUC | 0.9380 | 0.9358 | 0.9372 |
| ROC AUC | 0.9655 | 0.9605 | 0.9619 |
| F1 | 0.8647 | 0.8727 | 0.8664 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9655 -> 0.9619
