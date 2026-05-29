# Confirm PASS — bbdcd8db2263845a on `filetypes/data`

Cycle `20260526T205322-confirm-bbdcd8db2263845a` — 2026-05-26T20:53:22Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `bbdcd8db2263845a` | `bb733e2e2c63b243` | `bb733e2e2c63b243` | `bb733e2e2c63b243` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 1.0000 | 1.0000 | 1.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=bbdcd8db2263845a
```
