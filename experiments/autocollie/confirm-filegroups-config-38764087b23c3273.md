# Confirm PASS — 38764087b23c3273 on `filegroups/config`

Cycle `20260526T145837-confirm-38764087b23c3273` — 2026-05-26T14:58:37Z

PR_AUC held across 3 seeds (orig 0.9997)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `38764087b23c3273` | `9b5b8d89c6b742a4` | `9b5b8d89c6b742a4` | `9b5b8d89c6b742a4` |
| PR AUC | 0.9997 | 0.9998 | 0.9998 | 0.9999 |
| ROC AUC | 0.9995 | 0.9996 | 0.9997 | 0.9997 |
| Recall@3FPM | — | 0.8370 | 0.8378 | 0.9461 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=38764087b23c3273
```
