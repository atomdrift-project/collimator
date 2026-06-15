# Confirm PASS — 89648464dbf04d9a on `filetypes/pe`

Cycle `20260615T012314-confirm-89648464dbf04d9a` — 2026-06-15T01:23:14Z

PR_AUC held across 3 seeds (orig 0.9985)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `89648464dbf04d9a` | `5b11a6b14de729ba` | `5b11a6b14de729ba` | `5b11a6b14de729ba` |
| PR AUC | 0.9985 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9986 | 0.9995 | 0.9996 | 0.9995 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=89648464dbf04d9a
```
