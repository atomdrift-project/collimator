# Promote REJECTED — `0e1992a091171b0f` on `filetypes/crx`

Generated 2026-06-28T04:24:58Z

AUC regressed at full-train: 0.9966 -> 0.9936

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9966)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `0e1992a091171b0f` | `066b8b121909c2b2` | `2d0eeb228fc57d20` |
| PR AUC | 0.9966 | 0.9948 | 0.9937 |
| ROC AUC | 0.9966 | 0.9947 | 0.9936 |
| F1 | 0.9091 | 0.9405 | 0.9349 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9966 -> 0.9936
