# Confirm PASS — 4bb38600bbd3a41d on `filetypes/kotlin`

Cycle `20260609T070907-confirm-4bb38600bbd3a41d` — 2026-06-09T07:09:07Z

PR_AUC held across 3 seeds (orig 0.9994)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `4bb38600bbd3a41d` | `fb9f0378081c520a` | `fb9f0378081c520a` | `fb9f0378081c520a` |
| PR AUC | 0.9994 | 0.9998 | 0.9994 | 0.9993 |
| ROC AUC | 0.9755 | 0.9911 | 0.9778 | 0.9711 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=4bb38600bbd3a41d
```
