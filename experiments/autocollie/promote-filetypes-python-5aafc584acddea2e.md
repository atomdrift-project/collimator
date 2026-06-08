# Promote REJECTED — `5aafc584acddea2e` on `filetypes/python`

Generated 2026-06-08T18:29:54Z

AUC regressed at full-train: 0.9990 -> 0.9956

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9990)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `5aafc584acddea2e` | `5ca4361c5cffb42b` | `aac2175d37a89d3a` |
| PR AUC | 0.9990 | 0.9944 | 0.9947 |
| ROC AUC | 0.9990 | 0.9955 | 0.9956 |
| F1 | 0.9820 | 0.9649 | 0.9487 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9990 -> 0.9956
