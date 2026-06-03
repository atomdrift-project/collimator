# Confirm PASS — 0b0cce45b1dcd49f on `filegroups/scripts`

Cycle `20260603T161630-confirm-0b0cce45b1dcd49f` — 2026-06-03T16:16:30Z

PR_AUC held across 3 seeds (orig 0.9978)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0b0cce45b1dcd49f` | `a4335c4c7b950683` | `a4335c4c7b950683` | `a4335c4c7b950683` |
| PR AUC | 0.9978 | 0.9991 | 0.9991 | 0.9991 |
| ROC AUC | 0.9975 | 0.9989 | 0.9988 | 0.9989 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0b0cce45b1dcd49f
```
