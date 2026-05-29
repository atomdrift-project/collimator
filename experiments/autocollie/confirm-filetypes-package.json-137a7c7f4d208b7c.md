# Confirm PASS — 137a7c7f4d208b7c on `filetypes/package.json`

Cycle `20260526T182355-confirm-137a7c7f4d208b7c` — 2026-05-26T18:23:55Z

PR_AUC held across 3 seeds (orig 0.9998)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `137a7c7f4d208b7c` | `9ac2ff01b71baecb` | `9ac2ff01b71baecb` | `9ac2ff01b71baecb` |
| PR AUC | 0.9998 | 0.9999 | 0.9998 | 0.9996 |
| ROC AUC | 0.9996 | 0.9998 | 0.9997 | 0.9992 |
| Recall@3FPM | — | 0.9665 | 0.9673 | 0.9678 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=137a7c7f4d208b7c
```
