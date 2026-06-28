# Confirm PASS — c0d6529324310b84 on `filegroups/portable`

Cycle `20260628T115836-confirm-c0d6529324310b84` — 2026-06-28T11:58:36Z

PR_AUC held across 3 seeds (orig 0.9856)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c0d6529324310b84` | `c51f4d7c951be066` | `c51f4d7c951be066` | `c51f4d7c951be066` |
| PR AUC | 0.9856 | 0.9923 | 0.9917 | 0.9922 |
| ROC AUC | 0.9973 | 0.9983 | 0.9981 | 0.9982 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=c0d6529324310b84
```
