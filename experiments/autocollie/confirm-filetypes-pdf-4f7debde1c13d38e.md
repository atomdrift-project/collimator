# Confirm PASS — 4f7debde1c13d38e on `filetypes/pdf`

Cycle `20260705T174754-confirm-4f7debde1c13d38e` — 2026-07-05T17:47:54Z

PR_AUC held across 3 seeds (orig 0.9910)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `4f7debde1c13d38e` | `e4450e1c657e7d0e` | `e4450e1c657e7d0e` | `e4450e1c657e7d0e` |
| PR AUC | 0.9910 | 0.9937 | 0.9902 | 0.9943 |
| ROC AUC | 0.9742 | 0.9611 | 0.9384 | 0.9644 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=4f7debde1c13d38e
```
