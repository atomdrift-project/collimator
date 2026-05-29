# Promote REJECTED — `d1c62887c70337c0` on `filetypes/python-bytecode`

Generated 2026-05-26T22:52:27Z

AUC regressed at full-train: 0.9974 -> 0.9950

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9996)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `d1c62887c70337c0` | `0391bd501688ba8e` | `b9bff52f881dd4a8` |
| PR AUC | 0.9996 | 0.9985 | 0.9988 |
| ROC AUC | 0.9974 | 0.9940 | 0.9950 |
| F1 | 0.8864 | 0.9918 | 0.9918 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9974 -> 0.9950
