# Confirm PASS — 2649ea38c97bec6b on `filegroups/documents`

Cycle `20260613T182307-confirm-2649ea38c97bec6b` — 2026-06-13T18:23:07Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `2649ea38c97bec6b` | `acc256d4c95fc087` | `acc256d4c95fc087` | `acc256d4c95fc087` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9997 | 0.9991 | 0.9991 | 0.9991 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=2649ea38c97bec6b
```
