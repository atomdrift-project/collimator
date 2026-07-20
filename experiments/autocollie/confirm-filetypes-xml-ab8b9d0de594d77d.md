# Confirm PASS — ab8b9d0de594d77d on `filetypes/xml`

Cycle `20260709T110851-confirm-ab8b9d0de594d77d` — 2026-07-09T11:08:51Z

PR_AUC held across 3 seeds (orig 0.9995)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ab8b9d0de594d77d` | `a18bd79a8fe3a322` | `a18bd79a8fe3a322` | `a18bd79a8fe3a322` |
| PR AUC | 0.9995 | 0.9985 | 0.9970 | 0.9995 |
| ROC AUC | 0.9999 | 0.9996 | 0.9991 | 0.9999 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=ab8b9d0de594d77d
```
