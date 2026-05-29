# Confirm PASS — efdef5cc358a0cd7 on `filetypes/xls`

Cycle `20260526T175637-confirm-efdef5cc358a0cd7` — 2026-05-26T17:56:37Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `efdef5cc358a0cd7` | `3c21ced56315c5fd` | `3c21ced56315c5fd` | `3c21ced56315c5fd` |
| PR AUC | 0.9999 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9996 | 0.9996 | 0.9996 | 0.9996 |
| Recall@3FPM | — | 0.9864 | 0.9887 | 0.9879 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=efdef5cc358a0cd7
```
