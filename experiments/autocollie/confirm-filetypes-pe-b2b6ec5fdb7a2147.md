# Confirm PASS — b2b6ec5fdb7a2147 on `filetypes/pe`

Cycle `20260704T154623-confirm-b2b6ec5fdb7a2147` — 2026-07-04T15:46:23Z

PR_AUC held across 3 seeds (orig 0.9983)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b2b6ec5fdb7a2147` | `0028d117e7258158` | `0028d117e7258158` | `0028d117e7258158` |
| PR AUC | 0.9983 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9984 | 0.9993 | 0.9993 | 0.9993 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b2b6ec5fdb7a2147
```
