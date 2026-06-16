# Confirm PASS — e226cfa3c257e4b3 on `filegroups/config`

Cycle `20260616T100830-confirm-e226cfa3c257e4b3` — 2026-06-16T10:08:30Z

PR_AUC held across 3 seeds (orig 0.9989)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e226cfa3c257e4b3` | `50d540f80754b47f` | `50d540f80754b47f` | `50d540f80754b47f` |
| PR AUC | 0.9989 | 0.9989 | 0.9988 | 0.9986 |
| ROC AUC | 0.9985 | 0.9986 | 0.9984 | 0.9981 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e226cfa3c257e4b3
```
