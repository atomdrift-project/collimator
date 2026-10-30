# Confirm PASS — d9c6863d435e4f50 on `filetypes/registry`

Cycle `20261030T133940-confirm-d9c6863d435e4f50` — 2026-10-30T13:39:40Z

averaged 3-seed ensemble PR_AUC held: 0.9574 -> 0.9606; individual seeds may be noisy

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d9c6863d435e4f50` | `e5167b74bf767a47` | `e5167b74bf767a47` | `e5167b74bf767a47` |
| PR AUC | 0.9574 | 0.9630 | 0.9597 | 0.9561 |
| ROC AUC | 0.9996 | 0.9997 | 0.9997 | 0.9996 |
| Recall@L50 | — | 0.8393 | 0.8214 | 0.8393 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d9c6863d435e4f50
```
