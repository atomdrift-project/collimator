# Promote REJECTED — `b1651b24df6777b5` on `filegroups/media`

Generated 2026-11-12T20:31:48Z

PR_AUC regressed at full-train: 0.9724 -> 0.9478

## Gates

- **Confirm** (different seed, original profile): **PASS** — averaged 3-seed ensemble PR_AUC held: 0.9724 -> 0.9796; individual seeds may be noisy
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `b1651b24df6777b5` | `a34d9a1fcf8b666a` | `3b210d126e401aca` |
| PR AUC | 0.9724 | 0.9796 | 0.9478 |
| ROC AUC | 0.9955 | 0.9970 | 0.9966 |
| F1 | 0.9244 | 0.9383 | 0.8933 |

## Disposition

This spec did not survive the promotion ladder.

PR_AUC regressed at full-train: 0.9724 -> 0.9478
