# Promote REJECTED — `e789cb47deff697c` on `filetypes/lnk`

Generated 2026-05-27T00:02:06Z

AUC regressed at full-train: 0.9869 -> 0.9853

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9990)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `e789cb47deff697c` | `8bd61d09d25e9acf` | `ed3d70f93cdf85c3` |
| PR AUC | 0.9990 | 0.9988 | 0.9989 |
| ROC AUC | 0.9869 | 0.9846 | 0.9853 |
| F1 | 0.9814 | 0.9848 | 0.9848 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9869 -> 0.9853
