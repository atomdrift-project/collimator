# Confirm PASS — 650c2fe85c8b7928 on `filegroups/config`

Cycle `20260526T143824-confirm-650c2fe85c8b7928` — 2026-05-26T14:38:24Z

PR_AUC held across 3 seeds (orig 0.9997)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `650c2fe85c8b7928` | `14cd318f1ff478d0` | `14cd318f1ff478d0` | `14cd318f1ff478d0` |
| PR AUC | 0.9997 | 0.9997 | 0.9997 | 0.9998 |
| ROC AUC | 0.9995 | 0.9993 | 0.9995 | 0.9996 |
| Recall@3FPM | — | 0.9117 | 0.9361 | 0.9452 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=650c2fe85c8b7928
```
