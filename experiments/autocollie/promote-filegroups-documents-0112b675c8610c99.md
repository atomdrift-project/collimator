# Promote REJECTED — `0112b675c8610c99` on `filegroups/documents`

Generated 2026-05-23T19:26:30Z

AUC regressed at full-train: 0.9985 -> 0.9856

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `0112b675c8610c99` | `e916fda5f040c9d0` | `6a74dced793d190a` |
| PR AUC | 1.0000 | 0.9987 | 0.9999 |
| ROC AUC | 0.9985 | 0.9019 | 0.9856 |
| F1 | 0.9969 | 0.9965 | 0.9965 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9985 -> 0.9856
