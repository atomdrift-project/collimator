# Confirm PASS — 13a7af0711269e14 on `filegroups/portable`

Cycle `20260720T040523-confirm-13a7af0711269e14` — 2026-07-20T04:05:23Z

PR_AUC held across 3 seeds (orig 0.9913)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `13a7af0711269e14` | `2cd1fc2b538d2f0a` | `2cd1fc2b538d2f0a` | `2cd1fc2b538d2f0a` |
| PR AUC | 0.9913 | 0.9927 | 0.9916 | 0.9925 |
| ROC AUC | 0.9972 | 0.9977 | 0.9973 | 0.9980 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=13a7af0711269e14
```
