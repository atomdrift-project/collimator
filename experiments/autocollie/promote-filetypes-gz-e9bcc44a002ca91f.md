# Promote REJECTED — `e9bcc44a002ca91f` on `filetypes/gz`

Generated 2026-05-26T20:52:52Z

AUC regressed at full-train: 1.0000 -> 0.9979

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `e9bcc44a002ca91f` | `f9a7cb9485105faa` | `beaf8cbfc8400aa1` |
| PR AUC | 1.0000 | 0.9984 | 0.9984 |
| ROC AUC | 1.0000 | 0.9979 | 0.9979 |
| F1 | 0.6154 | 0.9956 | 0.9956 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 1.0000 -> 0.9979
