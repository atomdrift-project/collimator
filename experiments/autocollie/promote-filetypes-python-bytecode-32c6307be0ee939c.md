# Promote REJECTED — `32c6307be0ee939c` on `filetypes/python-bytecode`

Generated 2026-05-26T22:56:24Z

AUC regressed at full-train: 0.9923 -> 0.9911

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9988)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `32c6307be0ee939c` | `9f2d69804bd4c65f` | `48761605b7774e93` |
| PR AUC | 0.9988 | 0.9981 | 0.9979 |
| ROC AUC | 0.9923 | 0.9920 | 0.9911 |
| F1 | 0.8864 | 0.9918 | 0.9918 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9923 -> 0.9911
