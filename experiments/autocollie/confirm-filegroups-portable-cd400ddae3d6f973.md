# Confirm PASS — cd400ddae3d6f973 on `filegroups/portable`

Cycle `20260713T214554-confirm-cd400ddae3d6f973` — 2026-07-13T21:45:54Z

PR_AUC held across 3 seeds (orig 0.9947)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `cd400ddae3d6f973` | `908f1b67f7580a83` | `908f1b67f7580a83` | `908f1b67f7580a83` |
| PR AUC | 0.9947 | 0.9924 | 0.9935 | 0.9924 |
| ROC AUC | 0.9987 | 0.9975 | 0.9980 | 0.9977 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=cd400ddae3d6f973
```
