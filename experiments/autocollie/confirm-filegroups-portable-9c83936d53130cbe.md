# Confirm PASS — 9c83936d53130cbe on `filegroups/portable`

Cycle `20260525T211554-confirm-9c83936d53130cbe` — 2026-05-25T21:15:54Z

PR_AUC held across 3 seeds (orig 0.9967)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `9c83936d53130cbe` | `a24e8feacfcf1609` | `a24e8feacfcf1609` | `a24e8feacfcf1609` |
| PR AUC | 0.9967 | 0.9960 | 0.9948 | 0.9957 |
| ROC AUC | 0.9992 | 0.9990 | 0.9988 | 0.9989 |
| Recall@3FPM | — | 0.8200 | 0.7000 | 0.8667 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=9c83936d53130cbe
```
