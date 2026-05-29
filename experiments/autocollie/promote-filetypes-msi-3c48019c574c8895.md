# Promote REJECTED — `3c48019c574c8895` on `filetypes/msi`

Generated 2026-05-26T21:50:36Z

AUC regressed at full-train: 1.0000 -> 0.9973

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `3c48019c574c8895` | `0f5ac6d9fe86b9f1` | `2a93ffceb8c49ff9` |
| PR AUC | 1.0000 | 0.9996 | 0.9999 |
| ROC AUC | 1.0000 | 0.9870 | 0.9973 |
| F1 | 0.9892 | 0.9901 | 0.9967 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 1.0000 -> 0.9973
