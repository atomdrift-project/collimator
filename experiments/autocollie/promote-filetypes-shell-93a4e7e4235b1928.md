# Promote REJECTED — `93a4e7e4235b1928` on `filetypes/shell`

Generated 2026-05-27T01:05:28Z

AUC regressed at full-train: 0.9996 -> 0.9981

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9986)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `93a4e7e4235b1928` | `b2f9c8bedfdd90ad` | `8896488231819b69` |
| PR AUC | 0.9986 | 0.9972 | 0.9972 |
| ROC AUC | 0.9996 | 0.9981 | 0.9981 |
| F1 | 0.9755 | 0.9723 | 0.9702 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9996 -> 0.9981
