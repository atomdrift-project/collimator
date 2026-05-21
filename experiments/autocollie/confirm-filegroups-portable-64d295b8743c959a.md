# Confirm PASS — 64d295b8743c959a on `filegroups/portable`

Cycle `20260520T184329-confirm-64d295b8743c959a` — 2026-05-20T18:43:29Z

PR_AUC held across 3 seeds (orig 0.9967)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `64d295b8743c959a` | `36faffff0426af0e` | `36faffff0426af0e` | `36faffff0426af0e` |
| PR AUC | 0.9967 | 0.9942 | 0.9959 | 0.9963 |
| ROC AUC | 0.9992 | 0.9987 | 0.9990 | 0.9991 |
| Recall@3FPM | — | 0.5867 | 0.7733 | 0.8533 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=64d295b8743c959a
```
