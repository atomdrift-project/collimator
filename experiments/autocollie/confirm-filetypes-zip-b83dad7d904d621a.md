# Confirm PASS — b83dad7d904d621a on `filetypes/zip`

Cycle `20260711T164816-confirm-b83dad7d904d621a` — 2026-07-11T16:48:16Z

PR_AUC held across 3 seeds (orig 0.9987)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b83dad7d904d621a` | `06988b9762c45f64` | `06988b9762c45f64` | `06988b9762c45f64` |
| PR AUC | 0.9987 | 0.9989 | 0.9990 | 0.9990 |
| ROC AUC | 0.9944 | 0.9952 | 0.9954 | 0.9953 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b83dad7d904d621a
```
