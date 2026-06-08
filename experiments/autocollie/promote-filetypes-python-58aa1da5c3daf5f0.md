# Promote REJECTED — `58aa1da5c3daf5f0` on `filetypes/python`

Generated 2026-06-08T18:29:34Z

AUC regressed at full-train: 0.9990 -> 0.9956

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9990)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `58aa1da5c3daf5f0` | `dbb82e87fad027c8` | `ae70c2efbad9ac15` |
| PR AUC | 0.9990 | 0.9944 | 0.9945 |
| ROC AUC | 0.9990 | 0.9954 | 0.9956 |
| F1 | 0.9841 | 0.9555 | 0.9505 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9990 -> 0.9956
