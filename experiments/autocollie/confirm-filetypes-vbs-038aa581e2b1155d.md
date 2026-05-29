# Confirm PASS — 038aa581e2b1155d on `filetypes/vbs`

Cycle `20260526T222936-confirm-038aa581e2b1155d` — 2026-05-26T22:29:36Z

PR_AUC held across 3 seeds (orig 0.9995)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `038aa581e2b1155d` | `e6ca7b2319f6d461` | `e6ca7b2319f6d461` | `e6ca7b2319f6d461` |
| PR AUC | 0.9995 | 0.9973 | 0.9951 | 0.9958 |
| ROC AUC | 0.9993 | 0.9817 | 0.9777 | 0.9781 |
| Recall@3FPM | — | 0.3902 | 0.1286 | 0.1907 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=038aa581e2b1155d
```
