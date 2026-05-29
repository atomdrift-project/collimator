# Confirm PASS — b4565bcd605bcd62 on `filetypes/xls`

Cycle `20260526T183606-confirm-b4565bcd605bcd62` — 2026-05-26T18:36:06Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b4565bcd605bcd62` | `93b3d45445d05866` | `93b3d45445d05866` | `93b3d45445d05866` |
| PR AUC | 0.9999 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9996 | 0.9996 | 0.9996 | 0.9996 |
| Recall@3FPM | — | 0.9811 | 0.9841 | 0.9856 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b4565bcd605bcd62
```
