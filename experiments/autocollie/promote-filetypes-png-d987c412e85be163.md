# Promote REJECTED — `d987c412e85be163` on `filetypes/png`

Generated 2026-10-29T03:06:01Z

PR_AUC regressed at full-train: 0.9617 -> 0.9524

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9617)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `d987c412e85be163` | `20a820b26696738e` | `10c8c113589c90a8` |
| PR AUC | 0.9617 | 0.9748 | 0.9524 |
| ROC AUC | 0.9898 | 0.9946 | 0.9940 |
| F1 | 0.9236 | 0.9276 | 0.8927 |

## Disposition

This spec did not survive the promotion ladder.

PR_AUC regressed at full-train: 0.9617 -> 0.9524
