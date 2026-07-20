# Confirm PASS — 7b5fe7fc9b79192e on `filetypes/xls`

Cycle `20260710T232242-confirm-7b5fe7fc9b79192e` — 2026-07-10T23:22:42Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `7b5fe7fc9b79192e` | `6cd9e86f25478b3c` | `6cd9e86f25478b3c` | `6cd9e86f25478b3c` |
| PR AUC | 1.0000 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9992 | 0.9990 | 0.9990 | 0.9990 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=7b5fe7fc9b79192e
```
