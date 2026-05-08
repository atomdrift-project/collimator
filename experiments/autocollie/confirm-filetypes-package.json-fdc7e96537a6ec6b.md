# Confirm PASS — fdc7e96537a6ec6b on `filetypes/package.json`

Cycle `20260508T022550-confirm-fdc7e96537a6ec6b` — 2026-05-08T02:25:50Z

F1 held across 3 seeds (orig 0.9987)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `fdc7e96537a6ec6b` | `a79ba4d5523c9834` | `6c9a5c2847a8249e` | `4d12b063fc0c7912` |
| F1 | 0.9987 | 0.9981 | 0.9984 | 0.9984 |
| ROC AUC | 0.9998 | 0.9998 | 0.9998 | 0.9998 |
| AP | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| recall@3 FP/M | 0.9039 | 0.9247 | 0.9263 | 0.9242 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=fdc7e96537a6ec6b
```
