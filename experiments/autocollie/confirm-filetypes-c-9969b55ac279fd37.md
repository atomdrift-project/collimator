# Confirm PASS — 9969b55ac279fd37 on `filetypes/c`

Cycle `20260528T094020-confirm-9969b55ac279fd37` — 2026-05-28T09:40:20Z

PR_AUC held across 3 seeds (orig 0.9902)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `9969b55ac279fd37` | `f7a54380697f8b7d` | `f7a54380697f8b7d` | `f7a54380697f8b7d` |
| PR AUC | 0.9902 | 0.9906 | 0.9897 | 0.9909 |
| ROC AUC | 0.9951 | 0.9953 | 0.9946 | 0.9955 |
| Recall@3FPM | — | 0.7450 | 0.7651 | 0.7517 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=9969b55ac279fd37
```
