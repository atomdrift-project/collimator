# Promote REJECTED — `780698fd141c4f78` on `filetypes/python-bytecode`

Generated 2026-05-26T22:52:39Z

AUC regressed at full-train: 0.9974 -> 0.9946

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9996)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `780698fd141c4f78` | `ea98670b79638d4f` | `3f945dafb6ca74b0` |
| PR AUC | 0.9996 | 0.9983 | 0.9986 |
| ROC AUC | 0.9974 | 0.9935 | 0.9946 |
| F1 | 0.8989 | 0.9918 | 0.9918 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9974 -> 0.9946
