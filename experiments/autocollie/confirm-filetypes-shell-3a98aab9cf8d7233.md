# Confirm PASS — 3a98aab9cf8d7233 on `filetypes/shell`

Cycle `20260710T221028-confirm-3a98aab9cf8d7233` — 2026-07-10T22:10:28Z

PR_AUC held across 3 seeds (orig 0.9903)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3a98aab9cf8d7233` | `b1853891d501e035` | `b1853891d501e035` | `b1853891d501e035` |
| PR AUC | 0.9903 | 0.9920 | 0.9916 | 0.9925 |
| ROC AUC | 0.9942 | 0.9951 | 0.9947 | 0.9953 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3a98aab9cf8d7233
```
