# Confirm PASS — 50c4975d8ebeee2e on `filetypes/python-bytecode`

Cycle `20260525T203325-confirm-50c4975d8ebeee2e` — 2026-05-25T20:33:25Z

PR_AUC held across 3 seeds (orig 0.9993)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `50c4975d8ebeee2e` | `6770c0c24384f2bb` | `6770c0c24384f2bb` | `6770c0c24384f2bb` |
| PR AUC | 0.9993 | 0.9995 | 0.9992 | 0.9993 |
| ROC AUC | 0.9973 | 0.9981 | 0.9966 | 0.9971 |
| Recall@3FPM | — | 0.9796 | 0.9469 | 0.9796 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=50c4975d8ebeee2e
```
