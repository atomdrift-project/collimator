# Confirm PASS — b71f8e50aa30de46 on `filegroups/source`

Cycle `20260606T145443-confirm-b71f8e50aa30de46` — 2026-06-06T14:54:43Z

PR_AUC held across 3 seeds (orig 0.9990)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b71f8e50aa30de46` | `9da4d61d77548ec7` | `9da4d61d77548ec7` | `9da4d61d77548ec7` |
| PR AUC | 0.9990 | 0.9985 | 0.9983 | 0.9984 |
| ROC AUC | 0.9982 | 0.9979 | 0.9977 | 0.9978 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b71f8e50aa30de46
```
