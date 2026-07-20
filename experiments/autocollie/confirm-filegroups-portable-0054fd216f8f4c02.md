# Confirm PASS — 0054fd216f8f4c02 on `filegroups/portable`

Cycle `20260711T181647-confirm-0054fd216f8f4c02` — 2026-07-11T18:16:47Z

PR_AUC held across 3 seeds (orig 0.9924)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0054fd216f8f4c02` | `3d770df032fac4b6` | `3d770df032fac4b6` | `3d770df032fac4b6` |
| PR AUC | 0.9924 | 0.9934 | 0.9928 | 0.9923 |
| ROC AUC | 0.9981 | 0.9976 | 0.9982 | 0.9977 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0054fd216f8f4c02
```
