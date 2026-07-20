# Confirm PASS — 719acf67d9010821 on `filetypes/xlsx`

Cycle `20260713T214442-confirm-719acf67d9010821` — 2026-07-13T21:44:42Z

PR_AUC held across 3 seeds (orig 0.9953)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `719acf67d9010821` | `5977e0ad2db907c5` | `5977e0ad2db907c5` | `5977e0ad2db907c5` |
| PR AUC | 0.9953 | 0.9953 | 0.9953 | 0.9953 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=719acf67d9010821
```
