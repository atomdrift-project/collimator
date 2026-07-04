# Confirm PASS — 38764087b23c3273 on `filegroups/config`

Cycle `20260704T125104-confirm-38764087b23c3273` — 2026-07-04T12:51:04Z

PR_AUC held across 3 seeds (orig 0.9997)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `38764087b23c3273` | `864d1b0e38c364a9` | `864d1b0e38c364a9` | `864d1b0e38c364a9` |
| PR AUC | 0.9997 | 0.9979 | 0.9981 | 0.9981 |
| ROC AUC | 0.9995 | 0.9979 | 0.9981 | 0.9981 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=38764087b23c3273
```
