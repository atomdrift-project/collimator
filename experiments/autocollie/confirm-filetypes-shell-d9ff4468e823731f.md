# Confirm PASS — d9ff4468e823731f on `filetypes/shell`

Cycle `20260713T144742-confirm-d9ff4468e823731f` — 2026-07-13T14:47:42Z

PR_AUC held across 3 seeds (orig 0.9914)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d9ff4468e823731f` | `e1318c239057ae5b` | `e1318c239057ae5b` | `e1318c239057ae5b` |
| PR AUC | 0.9914 | 0.9909 | 0.9918 | 0.9913 |
| ROC AUC | 0.9947 | 0.9941 | 0.9949 | 0.9946 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d9ff4468e823731f
```
