# Confirm PASS — 3144621d465656c5 on `filetypes/javascript`

Cycle `20260521T183653-confirm-3144621d465656c5` — 2026-05-21T18:36:53Z

PR_AUC held across 3 seeds (orig 0.9993)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3144621d465656c5` | `f35682ec94bfacb7` | `f35682ec94bfacb7` | `f35682ec94bfacb7` |
| PR AUC | 0.9993 | 0.9996 | 0.9997 | 0.9997 |
| ROC AUC | 0.9989 | 0.9994 | 0.9995 | 0.9994 |
| Recall@3FPM | — | 0.8856 | 0.8922 | 0.9130 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3144621d465656c5
```
