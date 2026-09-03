# Promote REJECTED — `d3569d2c0c3a15f1` on `filetypes/gem`

Generated 2026-08-24T21:24:23Z

AUC regressed at full-train: 0.9955 -> 0.9915

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9902)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `d3569d2c0c3a15f1` | `cb7e250990a5f3a6` | `e9dfaada6cbbe54d` |
| PR AUC | 0.9902 | 0.9871 | 0.9862 |
| ROC AUC | 0.9955 | 0.9924 | 0.9915 |
| F1 | 0.9573 | 0.9815 | 0.9815 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9955 -> 0.9915
