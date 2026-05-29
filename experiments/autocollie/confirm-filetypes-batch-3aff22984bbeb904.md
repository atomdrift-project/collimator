# Confirm PASS — 3aff22984bbeb904 on `filetypes/batch`

Cycle `20260526T223004-confirm-3aff22984bbeb904` — 2026-05-26T22:30:04Z

PR_AUC held across 3 seeds (orig 0.9997)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3aff22984bbeb904` | `73ab6a3599199be2` | `73ab6a3599199be2` | `73ab6a3599199be2` |
| PR AUC | 0.9997 | 0.9995 | 0.9995 | 0.9996 |
| ROC AUC | 0.9977 | 0.9959 | 0.9960 | 0.9961 |
| Recall@3FPM | — | 0.9426 | 0.9765 | 0.9765 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3aff22984bbeb904
```
