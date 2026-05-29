# Promote REJECTED — `9b75ff23f8a1a8e0` on `filetypes/chrome-manifest`

Generated 2026-05-25T21:21:06Z

PR_AUC regressed at full-train: 0.8769 -> 0.8588

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.8769)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `9b75ff23f8a1a8e0` | `961709eb00d4087c` | `fcb2e28d1f892bf8` |
| PR AUC | 0.8769 | 0.8833 | 0.8588 |
| ROC AUC | 0.9590 | 0.9641 | 0.9385 |
| F1 | 0.8000 | 0.8889 | 0.8889 |

## Disposition

This spec did not survive the promotion ladder.

PR_AUC regressed at full-train: 0.8769 -> 0.8588
