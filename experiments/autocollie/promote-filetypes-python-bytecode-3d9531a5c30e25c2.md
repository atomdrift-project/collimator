# Promote REJECTED — `3d9531a5c30e25c2` on `filetypes/python-bytecode`

Generated 2026-05-26T22:52:51Z

AUC regressed at full-train: 0.9974 -> 0.9957

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9996)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `3d9531a5c30e25c2` | `d1f17a9708d72c3d` | `a316f7831b60c8cb` |
| PR AUC | 0.9996 | 0.9987 | 0.9990 |
| ROC AUC | 0.9974 | 0.9946 | 0.9957 |
| F1 | 0.8989 | 0.9918 | 0.9918 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9974 -> 0.9957
