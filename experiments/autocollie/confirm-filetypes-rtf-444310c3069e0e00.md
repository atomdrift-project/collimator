# Confirm PASS — 444310c3069e0e00 on `filetypes/rtf`

Cycle `20260711T090709-confirm-444310c3069e0e00` — 2026-07-11T09:07:09Z

PR_AUC held across 3 seeds (orig 0.9995)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `444310c3069e0e00` | `2d0d707812ddb78c` | `2d0d707812ddb78c` | `2d0d707812ddb78c` |
| PR AUC | 0.9995 | 0.9995 | 0.9995 | 0.9997 |
| ROC AUC | 0.9977 | 0.9976 | 0.9976 | 0.9985 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=444310c3069e0e00
```
