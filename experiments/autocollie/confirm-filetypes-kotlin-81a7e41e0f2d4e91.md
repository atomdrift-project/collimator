# Confirm PASS — 81a7e41e0f2d4e91 on `filetypes/kotlin`

Cycle `20260616T100110-confirm-81a7e41e0f2d4e91` — 2026-06-16T10:01:10Z

PR_AUC held across 3 seeds (orig 0.9993)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `81a7e41e0f2d4e91` | `729eebb0bae6c00c` | `729eebb0bae6c00c` | `729eebb0bae6c00c` |
| PR AUC | 0.9993 | 0.9999 | 0.9986 | 0.9987 |
| ROC AUC | 0.9737 | 0.9940 | 0.9549 | 0.9610 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=81a7e41e0f2d4e91
```
