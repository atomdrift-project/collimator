# Confirm PASS — b1121d062d1ee319 on `filetypes/lnk`

Cycle `20261110T105752-confirm-b1121d062d1ee319` — 2026-11-10T10:57:52Z

averaged 3-seed ensemble PR_AUC held: 0.9985 -> 0.9992; individual seeds may be noisy

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b1121d062d1ee319` | `e015482c80d791b5` | `e015482c80d791b5` | `e015482c80d791b5` |
| PR AUC | 0.9985 | 0.9994 | 0.9990 | 0.9988 |
| ROC AUC | 0.9946 | 0.9975 | 0.9961 | 0.9952 |
| Recall@L50 | — | 0.7945 | 0.7014 | 0.7560 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b1121d062d1ee319
```
