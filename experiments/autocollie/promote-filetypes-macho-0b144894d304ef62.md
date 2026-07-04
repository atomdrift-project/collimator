# Promote REJECTED — `0b144894d304ef62` on `filetypes/macho`

Generated 2026-07-04T13:59:43Z

AUC regressed at full-train: 0.9985 -> 0.9958

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9931)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `0b144894d304ef62` | `f3fa42be2e10fd1a` | `9a05e56f4f723c53` |
| PR AUC | 0.9931 | 0.9893 | 0.9893 |
| ROC AUC | 0.9985 | 0.9959 | 0.9958 |
| F1 | 0.9671 | 0.9678 | 0.9678 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9985 -> 0.9958
