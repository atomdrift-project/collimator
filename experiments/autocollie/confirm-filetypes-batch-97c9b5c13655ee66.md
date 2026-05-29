# Confirm PASS — 97c9b5c13655ee66 on `filetypes/batch`

Cycle `20260526T222815-confirm-97c9b5c13655ee66` — 2026-05-26T22:28:15Z

PR_AUC held across 3 seeds (orig 0.9998)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `97c9b5c13655ee66` | `d71092d7d2361102` | `d71092d7d2361102` | `d71092d7d2361102` |
| PR AUC | 0.9998 | 0.9996 | 0.9995 | 0.9996 |
| ROC AUC | 0.9980 | 0.9964 | 0.9961 | 0.9964 |
| Recall@3FPM | — | 0.9530 | 0.9765 | 0.9765 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=97c9b5c13655ee66
```
