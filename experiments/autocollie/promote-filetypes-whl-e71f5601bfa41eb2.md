# Promote REJECTED — `e71f5601bfa41eb2` on `filetypes/whl`

Generated 2026-07-13T21:51:34Z

AUC regressed at full-train: 0.9678 -> 0.9660

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9690)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `e71f5601bfa41eb2` | `e2c2054d962de0eb` | `550b6a44ad1f3d0c` |
| PR AUC | 0.9690 | 0.9695 | 0.9685 |
| ROC AUC | 0.9678 | 0.9684 | 0.9660 |
| F1 | 0.9082 | 0.9227 | 0.9225 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9678 -> 0.9660
