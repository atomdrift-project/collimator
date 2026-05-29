# Confirm PASS — 790ceff1ed59751d on `filetypes/python`

Cycle `20260526T233907-confirm-790ceff1ed59751d` — 2026-05-26T23:39:07Z

PR_AUC held across 3 seeds (orig 0.9991)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `790ceff1ed59751d` | `f572830b4139c837` | `f572830b4139c837` | `f572830b4139c837` |
| PR AUC | 0.9991 | 0.9985 | 0.9984 | 0.9986 |
| ROC AUC | 0.9991 | 0.9987 | 0.9986 | 0.9987 |
| Recall@3FPM | — | 0.8633 | 0.7266 | 0.7613 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=790ceff1ed59751d
```
