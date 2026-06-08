# Promote REJECTED — `5abd3b06ee3b5c82` on `filetypes/python`

Generated 2026-06-08T18:28:24Z

AUC regressed at full-train: 0.9992 -> 0.9960

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9992)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `5abd3b06ee3b5c82` | `e0af3df47c864016` | `d57480360c209b0c` |
| PR AUC | 0.9992 | 0.9947 | 0.9950 |
| ROC AUC | 0.9992 | 0.9956 | 0.9960 |
| F1 | 0.9849 | 0.9563 | 0.9488 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9992 -> 0.9960
