# Promote REJECTED — `3a0a62c1c0d293c1` on `filetypes/c`

Generated 2026-11-02T19:45:48Z

PR_AUC regressed at full-train: 0.9453 -> 0.8984

## Gates

- **Confirm** (different seed, original profile): **PASS** — averaged 3-seed ensemble PR_AUC held: 0.9453 -> 0.9531; individual seeds may be noisy
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `3a0a62c1c0d293c1` | `77999fadab9f8b67` | `cc38c093f6cb1a02` |
| PR AUC | 0.9453 | 0.9531 | 0.8984 |
| ROC AUC | 0.9803 | 0.9826 | 0.9824 |
| F1 | 0.8451 | 0.8803 | 0.8306 |

## Disposition

This spec did not survive the promotion ladder.

PR_AUC regressed at full-train: 0.9453 -> 0.8984
