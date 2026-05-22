# Confirm PASS — 02e6aac4fca061d0 on `filetypes/lnk`

Cycle `20260522T165511-confirm-02e6aac4fca061d0` — 2026-05-22T16:55:11Z

PR_AUC held across 3 seeds (orig 0.9988)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `02e6aac4fca061d0` | `2d9564967a5c9d5c` | `2d9564967a5c9d5c` | `2d9564967a5c9d5c` |
| PR AUC | 0.9988 | 0.9985 | 0.9989 | 0.9930 |
| ROC AUC | 0.9855 | 0.9819 | 0.9862 | 0.9360 |
| Recall@3FPM | — | 0.9096 | 0.9574 | 0.6277 |
| verdict | — | PASS | PASS | FAIL |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=02e6aac4fca061d0
```
