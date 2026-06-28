# Promote REJECTED — `65f71553d88b8f51` on `filetypes/shell`

Generated 2026-06-28T13:24:27Z

AUC regressed at full-train: 0.9966 -> 0.9943

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9949)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `65f71553d88b8f51` | `0dae45d16790bc4a` | `c090926267603c1c` |
| PR AUC | 0.9949 | 0.9924 | 0.9924 |
| ROC AUC | 0.9966 | 0.9943 | 0.9943 |
| F1 | 0.9339 | 0.9478 | 0.9495 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9966 -> 0.9943
