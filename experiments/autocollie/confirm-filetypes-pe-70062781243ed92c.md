# Confirm PASS — 70062781243ed92c on `filetypes/pe`

Cycle `20260606T043151-confirm-70062781243ed92c` — 2026-06-06T04:31:51Z

PR_AUC held across 3 seeds (orig 0.9995)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `70062781243ed92c` | `b6b6106898d83740` | `b6b6106898d83740` | `b6b6106898d83740` |
| PR AUC | 0.9995 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9995 | 0.9999 | 0.9999 | 0.9999 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=70062781243ed92c
```
