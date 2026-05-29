# Promote REJECTED — `8ebbdabe9ffa9182` on `filetypes/msi`

Generated 2026-05-26T21:50:44Z

AUC regressed at full-train: 1.0000 -> 0.9970

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `8ebbdabe9ffa9182` | `e93c3edc95835111` | `8fa2944f876cec62` |
| PR AUC | 1.0000 | 0.9999 | 0.9999 |
| ROC AUC | 1.0000 | 0.9970 | 0.9970 |
| F1 | 0.9892 | 0.9967 | 0.9967 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 1.0000 -> 0.9970
