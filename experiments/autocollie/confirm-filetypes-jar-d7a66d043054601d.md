# Confirm PASS — d7a66d043054601d on `filetypes/jar`

Cycle `20260527T000601-confirm-d7a66d043054601d` — 2026-05-27T00:06:01Z

PR_AUC held across 3 seeds (orig 0.9987)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d7a66d043054601d` | `f56b005bb3223996` | `f56b005bb3223996` | `f56b005bb3223996` |
| PR AUC | 0.9987 | 0.9971 | 0.9982 | 0.9978 |
| ROC AUC | 0.9975 | 0.9939 | 0.9966 | 0.9960 |
| Recall@3FPM | — | 0.8580 | 0.8636 | 0.8580 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d7a66d043054601d
```
