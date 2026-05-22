# Promote REJECTED — `0d0c6636d75dc0b9` on `filetypes/png`

Generated 2026-05-22T17:00:33Z

AUC regressed at full-train: 0.9731 -> 0.9706

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9867)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `0d0c6636d75dc0b9` | `4fe77bf95fb29bba` | `0fd46de69fae6bd9` |
| PR AUC | 0.9867 | 0.9843 | 0.9853 |
| ROC AUC | 0.9731 | 0.9688 | 0.9706 |
| F1 | 0.9524 | 0.9265 | 0.9197 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9731 -> 0.9706
