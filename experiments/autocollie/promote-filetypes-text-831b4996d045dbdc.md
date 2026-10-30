# Promote REJECTED — `831b4996d045dbdc` on `filetypes/text`

Generated 2026-10-30T19:29:18Z

PR_AUC regressed at full-train: 0.9180 -> 0.8757

## Gates

- **Confirm** (different seed, original profile): **PASS** — averaged 3-seed ensemble PR_AUC held: 0.9180 -> 0.9381; individual seeds may be noisy
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `831b4996d045dbdc` | `3546e3721884c8ec` | `f0a44611379d47bf` |
| PR AUC | 0.9180 | 0.9381 | 0.8757 |
| ROC AUC | 0.9842 | 0.9851 | 0.9861 |
| F1 | 0.7387 | 0.8911 | 0.7864 |

## Disposition

This spec did not survive the promotion ladder.

PR_AUC regressed at full-train: 0.9180 -> 0.8757
