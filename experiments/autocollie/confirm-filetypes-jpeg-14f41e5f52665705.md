# Confirm PASS — 14f41e5f52665705 on `filetypes/jpeg`

Cycle `20260603T161517-confirm-14f41e5f52665705` — 2026-06-03T16:15:17Z

PR_AUC held across 3 seeds (orig 0.9820)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `14f41e5f52665705` | `4f9574edcbf48f3a` | `4f9574edcbf48f3a` | `4f9574edcbf48f3a` |
| PR AUC | 0.9820 | 0.9640 | 0.9730 | 0.9828 |
| ROC AUC | 0.9904 | 0.9802 | 0.9856 | 0.9901 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=14f41e5f52665705
```
