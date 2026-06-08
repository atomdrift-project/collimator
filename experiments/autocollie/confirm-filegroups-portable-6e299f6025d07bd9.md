# Confirm PASS — 6e299f6025d07bd9 on `filegroups/portable`

Cycle `20260607T210144-confirm-6e299f6025d07bd9` — 2026-06-07T21:01:44Z

PR_AUC held across 3 seeds (orig 0.9895)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6e299f6025d07bd9` | `536051fca21c24b8` | `536051fca21c24b8` | `536051fca21c24b8` |
| PR AUC | 0.9895 | 0.9907 | 0.9892 | 0.9899 |
| ROC AUC | 0.9976 | 0.9980 | 0.9979 | 0.9981 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=6e299f6025d07bd9
```
