# Promote REJECTED — `038aa581e2b1155d` on `filetypes/vbs`

Generated 2026-05-26T22:29:40Z

AUC regressed at full-train: 0.9993 -> 0.9805

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9995)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `038aa581e2b1155d` | `e6ca7b2319f6d461` | `98ee01f917c8d11d` |
| PR AUC | 0.9995 | 0.9961 | 0.9964 |
| ROC AUC | 0.9993 | 0.9790 | 0.9805 |
| F1 | 0.2973 | 0.3389 | 0.3718 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9993 -> 0.9805
