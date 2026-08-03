# Confirm PASS — 403b3d7c80635af8 on `filetypes/jar`

Cycle `20260803T205918-confirm-403b3d7c80635af8` — 2026-08-03T20:59:18Z

PR_AUC held across 3 seeds (orig 0.9516)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `403b3d7c80635af8` | `564a7a0aed5aee4e` | `564a7a0aed5aee4e` | `564a7a0aed5aee4e` |
| PR AUC | 0.9516 | 0.9552 | 0.9579 | 0.9525 |
| ROC AUC | 0.9781 | 0.9771 | 0.9789 | 0.9792 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=403b3d7c80635af8
```
