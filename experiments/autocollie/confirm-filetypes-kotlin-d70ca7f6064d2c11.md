# Confirm PASS — d70ca7f6064d2c11 on `filetypes/kotlin`

Cycle `20260628T113535-confirm-d70ca7f6064d2c11` — 2026-06-28T11:35:35Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d70ca7f6064d2c11` | `cf5ff714a1449257` | `cf5ff714a1449257` | `cf5ff714a1449257` |
| PR AUC | 0.9999 | 0.9995 | 0.9998 | 0.9996 |
| ROC AUC | 0.9949 | 0.9832 | 0.9917 | 0.9874 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d70ca7f6064d2c11
```
