# Confirm PASS — 10296b93df5d6058 on `filegroups/archive`

Cycle `20260508T135909-confirm-10296b93df5d6058` — 2026-05-08T13:59:09Z

F1 held across 3 seeds (orig 0.9965)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `10296b93df5d6058` | `afec39915400a0b2` | `276289215abd5159` | `e04bf37934c902d4` |
| F1 | 0.9965 | 0.9963 | 0.9959 | 0.9965 |
| ROC AUC | 0.9999 | 0.9999 | 0.9999 | 0.9999 |
| AP | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| recall@3 FP/M | 0.9034 | 0.9562 | 0.9284 | 0.9514 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=10296b93df5d6058
```
