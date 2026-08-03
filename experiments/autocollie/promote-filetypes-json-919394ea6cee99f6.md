# Promote REJECTED — `919394ea6cee99f6` on `filetypes/json`

Generated 2026-07-23T06:21:03Z

AUC regressed at full-train: 0.9746 -> 0.9722

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9682)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `919394ea6cee99f6` | `2ad0f4e4acd7d6e3` | `cbb22670eaa281fe` |
| PR AUC | 0.9682 | 0.9667 | 0.9682 |
| ROC AUC | 0.9746 | 0.9698 | 0.9722 |
| F1 | 0.9057 | 0.9434 | 0.9434 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9746 -> 0.9722
