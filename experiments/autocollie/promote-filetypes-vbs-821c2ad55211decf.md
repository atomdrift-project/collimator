# Promote REJECTED — `821c2ad55211decf` on `filetypes/vbs`

Generated 2026-05-26T22:28:54Z

AUC regressed at full-train: 0.9993 -> 0.9805

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9995)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `821c2ad55211decf` | `6b640d15146cb440` | `f95cad815d53b656` |
| PR AUC | 0.9995 | 0.9961 | 0.9964 |
| ROC AUC | 0.9993 | 0.9790 | 0.9805 |
| F1 | 0.9692 | 0.9868 | 0.9889 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9993 -> 0.9805
