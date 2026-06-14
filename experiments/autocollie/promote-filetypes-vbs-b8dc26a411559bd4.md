# Promote REJECTED — `b8dc26a411559bd4` on `filetypes/vbs`

Generated 2026-06-14T04:49:50Z

AUC regressed at full-train: 0.9914 -> 0.9878

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9975)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `b8dc26a411559bd4` | `e88f560d9b2008a6` | `faa99f669292e9c4` |
| PR AUC | 0.9975 | 0.9969 | 0.9967 |
| ROC AUC | 0.9914 | 0.9885 | 0.9878 |
| F1 | 0.9586 | 0.9615 | 0.9746 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9914 -> 0.9878
