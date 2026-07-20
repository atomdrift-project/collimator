# Confirm PASS — 292544d0153a5132 on `filegroups/native`

Cycle `20260711T040610-confirm-292544d0153a5132` — 2026-07-11T04:06:10Z

PR_AUC held across 3 seeds (orig 0.9991)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `292544d0153a5132` | `375a408f33abd4f4` | `375a408f33abd4f4` | `375a408f33abd4f4` |
| PR AUC | 0.9991 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9991 | 0.9998 | 0.9998 | 0.9998 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=292544d0153a5132
```
