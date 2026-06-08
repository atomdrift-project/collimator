# Confirm PASS — 0d99089632189960 on `filetypes/xls`

Cycle `20260607T205353-confirm-0d99089632189960` — 2026-06-07T20:53:53Z

PR_AUC held across 3 seeds (orig 0.9998)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0d99089632189960` | `b098fb6d82670210` | `b098fb6d82670210` | `b098fb6d82670210` |
| PR AUC | 0.9998 | 0.9995 | 0.9998 | 0.9998 |
| ROC AUC | 0.9980 | 0.9963 | 0.9981 | 0.9983 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0d99089632189960
```
