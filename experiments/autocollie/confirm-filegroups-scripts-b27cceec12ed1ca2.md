# Confirm PASS — b27cceec12ed1ca2 on `filegroups/scripts`

Cycle `20260711T113559-confirm-b27cceec12ed1ca2` — 2026-07-11T11:35:59Z

PR_AUC held across 3 seeds (orig 0.9923)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b27cceec12ed1ca2` | `069918e7594954c7` | `069918e7594954c7` | `069918e7594954c7` |
| PR AUC | 0.9923 | 0.9949 | 0.9949 | 0.9948 |
| ROC AUC | 0.9906 | 0.9959 | 0.9959 | 0.9958 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b27cceec12ed1ca2
```
