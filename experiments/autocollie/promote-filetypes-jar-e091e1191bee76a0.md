# Promote REJECTED — `e091e1191bee76a0` on `filetypes/jar`

Generated 2026-05-21T04:22:39Z

AUC regressed at full-train: 0.9977 -> 0.9963

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9988)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `e091e1191bee76a0` | `ea71b95e3315b3c4` | `0f9995b38a8c934e` |
| PR AUC | 0.9988 | 0.9980 | 0.9981 |
| ROC AUC | 0.9977 | 0.9961 | 0.9963 |
| F1 | 0.9657 | 0.9769 | 0.9796 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9977 -> 0.9963
