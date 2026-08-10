# Promote REJECTED — `d1657a026b309e3d` on `filetypes/xlsx`

Generated 2026-08-05T14:56:00Z

AUC regressed at full-train: 0.8197 -> 0.8004

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9860)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `d1657a026b309e3d` | `3d225a1f4b804e7c` | `fd45fe4fe54446e8` |
| PR AUC | 0.9860 | 0.9891 | 0.9885 |
| ROC AUC | 0.8197 | 0.8100 | 0.8004 |
| F1 | 0.5210 | 0.9835 | 0.9838 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.8197 -> 0.8004
