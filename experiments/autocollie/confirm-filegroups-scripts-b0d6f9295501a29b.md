# Confirm PASS — b0d6f9295501a29b on `filegroups/scripts`

Cycle `20260613T195035-confirm-b0d6f9295501a29b` — 2026-06-13T19:50:35Z

PR_AUC held across 3 seeds (orig 0.9978)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b0d6f9295501a29b` | `29e227387d821e48` | `29e227387d821e48` | `29e227387d821e48` |
| PR AUC | 0.9978 | 0.9971 | 0.9971 | 0.9972 |
| ROC AUC | 0.9976 | 0.9967 | 0.9967 | 0.9968 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b0d6f9295501a29b
```
