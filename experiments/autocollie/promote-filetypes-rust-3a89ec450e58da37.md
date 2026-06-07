# Promote REJECTED — `3a89ec450e58da37` on `filetypes/rust`

Generated 2026-06-07T01:04:48Z

PR_AUC regressed at full-train: 0.9009 -> 0.8729

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9009)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `3a89ec450e58da37` | `75c15019d4b23481` | `bf2a3ae4cc6b55d3` |
| PR AUC | 0.9009 | 0.9237 | 0.8729 |
| ROC AUC | 0.9920 | 0.9944 | 0.9920 |
| F1 | 0.7407 | 0.9091 | 0.8750 |

## Disposition

This spec did not survive the promotion ladder.

PR_AUC regressed at full-train: 0.9009 -> 0.8729
