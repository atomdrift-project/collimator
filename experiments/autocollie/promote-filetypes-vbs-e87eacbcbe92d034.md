# Promote REJECTED — `e87eacbcbe92d034` on `filetypes/vbs`

Generated 2026-05-26T22:29:34Z

PR_AUC regressed at full-train: 0.9995 -> 0.9944

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9995)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `e87eacbcbe92d034` | `7d0815ce1b0df554` | `2e6b03cd13573cc5` |
| PR AUC | 0.9995 | 0.9949 | 0.9944 |
| ROC AUC | 0.9993 | 0.9745 | 0.9755 |
| F1 | 0.9920 | 0.9855 | 0.9835 |

## Disposition

This spec did not survive the promotion ladder.

PR_AUC regressed at full-train: 0.9995 -> 0.9944
