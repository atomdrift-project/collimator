# Confirm PASS — 7dbfe6fe0044799c on `filetypes/rtf`

Cycle `20260715T124254-confirm-7dbfe6fe0044799c` — 2026-07-15T12:42:54Z

PR_AUC held across 3 seeds (orig 0.9995)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `7dbfe6fe0044799c` | `fb3299d590862aac` | `fb3299d590862aac` | `fb3299d590862aac` |
| PR AUC | 0.9995 | 0.9997 | 0.9995 | 0.9997 |
| ROC AUC | 0.9976 | 0.9984 | 0.9976 | 0.9983 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=7dbfe6fe0044799c
```
