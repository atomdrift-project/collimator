# Confirm PASS — 6dda74a680861b4e on `filetypes/makefile`

Cycle `20260527T061820-confirm-6dda74a680861b4e` — 2026-05-27T06:18:20Z

PR_AUC held across 3 seeds (orig 0.0769)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6dda74a680861b4e` | `11458297a58978b2` | `11458297a58978b2` | `11458297a58978b2` |
| PR AUC | 0.0769 | 0.0769 | 0.0769 | 0.0769 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=6dda74a680861b4e
```
