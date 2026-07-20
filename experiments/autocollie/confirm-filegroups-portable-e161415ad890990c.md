# Confirm PASS — e161415ad890990c on `filegroups/portable`

Cycle `20260712T225927-confirm-e161415ad890990c` — 2026-07-12T22:59:27Z

PR_AUC held across 3 seeds (orig 0.9926)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e161415ad890990c` | `563a3052fc23cb69` | `563a3052fc23cb69` | `563a3052fc23cb69` |
| PR AUC | 0.9926 | 0.9938 | 0.9943 | 0.9932 |
| ROC AUC | 0.9980 | 0.9977 | 0.9985 | 0.9980 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e161415ad890990c
```
