# Promote REJECTED — `19b2e0952c1b0dc3` on `filetypes/crx`

Generated 2026-06-28T03:57:55Z

AUC regressed at full-train: 0.9966 -> 0.9936

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9966)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `19b2e0952c1b0dc3` | `df7aa4151ba6535e` | `5cef491d4bdc204d` |
| PR AUC | 0.9966 | 0.9948 | 0.9937 |
| ROC AUC | 0.9966 | 0.9947 | 0.9936 |
| F1 | 0.9091 | 0.9405 | 0.9349 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9966 -> 0.9936
