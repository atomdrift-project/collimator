# Promote REJECTED — `f41f682734dbb9cc` on `filetypes/python`

Generated 2026-06-13T23:39:07Z

AUC regressed at full-train: 0.9953 -> 0.9936

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9942)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `f41f682734dbb9cc` | `f29bf37d6ca1e980` | `f4c5d5df08531355` |
| PR AUC | 0.9942 | 0.9911 | 0.9911 |
| ROC AUC | 0.9953 | 0.9936 | 0.9936 |
| F1 | 0.9668 | 0.9520 | 0.9517 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9953 -> 0.9936
