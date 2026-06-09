# Confirm PASS — 282256a771c08dbf on `filetypes/rtf`

Cycle `20260609T095748-confirm-282256a771c08dbf` — 2026-06-09T09:57:48Z

PR_AUC held across 3 seeds (orig 0.9998)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `282256a771c08dbf` | `e6ecc324acd2aaae` | `e6ecc324acd2aaae` | `e6ecc324acd2aaae` |
| PR AUC | 0.9998 | 0.9998 | 0.9998 | 0.9998 |
| ROC AUC | 0.9984 | 0.9982 | 0.9980 | 0.9978 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=282256a771c08dbf
```
