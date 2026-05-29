# Confirm PASS — 06cb13f7cc75d854 on `filegroups/source`

Cycle `20260526T025830-confirm-06cb13f7cc75d854` — 2026-05-26T02:58:30Z

PR_AUC held across 3 seeds (orig 0.9988)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `06cb13f7cc75d854` | `e406720f7530bb26` | `e406720f7530bb26` | `e406720f7530bb26` |
| PR AUC | 0.9988 | 0.9992 | 0.9991 | 0.9992 |
| ROC AUC | 0.9981 | 0.9985 | 0.9984 | 0.9985 |
| Recall@3FPM | — | 0.9275 | 0.9398 | 0.9214 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=06cb13f7cc75d854
```
