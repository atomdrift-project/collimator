# Confirm PASS — f2fba1536fc537d0 on `filetypes/python`

Cycle `20260526T233431-confirm-f2fba1536fc537d0` — 2026-05-26T23:34:31Z

PR_AUC held across 3 seeds (orig 0.9989)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f2fba1536fc537d0` | `15426576c564e9d1` | `15426576c564e9d1` | `15426576c564e9d1` |
| PR AUC | 0.9989 | 0.9983 | 0.9983 | 0.9982 |
| ROC AUC | 0.9989 | 0.9985 | 0.9985 | 0.9984 |
| Recall@3FPM | — | 0.8003 | 0.7448 | 0.7202 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f2fba1536fc537d0
```
