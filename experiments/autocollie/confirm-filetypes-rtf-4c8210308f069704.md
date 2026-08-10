# Confirm PASS — 4c8210308f069704 on `filetypes/rtf`

Cycle `20260804T201024-confirm-4c8210308f069704` — 2026-08-04T20:10:24Z

PR_AUC held across 3 seeds (orig 0.9993)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `4c8210308f069704` | `c19fd3cff4f11cd9` | `c19fd3cff4f11cd9` | `c19fd3cff4f11cd9` |
| PR AUC | 0.9993 | 0.9992 | 0.9993 | 0.9993 |
| ROC AUC | 0.9964 | 0.9960 | 0.9960 | 0.9959 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=4c8210308f069704
```
