# Promote REJECTED — `7a9ddc3ac93cbf59` on `filetypes/json`

Generated 2026-11-12T12:24:16Z

PR_AUC regressed at full-train: 0.9635 -> 0.9477

## Gates

- **Confirm** (different seed, original profile): **PASS** — averaged 3-seed ensemble PR_AUC held: 0.9635 -> 0.9752; individual seeds may be noisy
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `7a9ddc3ac93cbf59` | `8bae31b0fa032ef6` | `b746fd73b55badaf` |
| PR AUC | 0.9635 | 0.9752 | 0.9477 |
| ROC AUC | 0.9966 | 0.9983 | 0.9988 |
| F1 | 0.9272 | 0.9659 | 0.9185 |

## Disposition

This spec did not survive the promotion ladder.

PR_AUC regressed at full-train: 0.9635 -> 0.9477
