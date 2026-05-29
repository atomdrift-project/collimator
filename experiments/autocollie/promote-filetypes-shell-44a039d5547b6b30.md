# Promote REJECTED — `44a039d5547b6b30` on `filetypes/shell`

Generated 2026-05-27T01:05:13Z

AUC regressed at full-train: 0.9996 -> 0.9979

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9984)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `44a039d5547b6b30` | `a29a2cfde7f19df4` | `2ac6f6cef4c0883a` |
| PR AUC | 0.9984 | 0.9971 | 0.9970 |
| ROC AUC | 0.9996 | 0.9980 | 0.9979 |
| F1 | 0.9754 | 0.9682 | 0.9689 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9996 -> 0.9979
