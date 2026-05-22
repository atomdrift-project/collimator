# Promote REJECTED — `b42606525fa9c7d9` on `filetypes/rust`

Generated 2026-05-22T17:40:22Z

PR_AUC regressed at full-train: 0.8239 -> 0.8078

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.8239)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `b42606525fa9c7d9` | `6d732b33dd3a2a96` | `3042ad70bc2293b0` |
| PR AUC | 0.8239 | 0.8250 | 0.8078 |
| ROC AUC | 0.9769 | 0.9818 | 0.9790 |
| F1 | 0.3750 | 0.7879 | 0.8125 |

## Disposition

This spec did not survive the promotion ladder.

PR_AUC regressed at full-train: 0.8239 -> 0.8078
