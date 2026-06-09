# Confirm PASS — ea83775b3e61c4b8 on `filegroups/scripts`

Cycle `20260609T105909-confirm-ea83775b3e61c4b8` — 2026-06-09T10:59:09Z

PR_AUC held across 3 seeds (orig 0.9962)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ea83775b3e61c4b8` | `6ab67c4240b62e99` | `6ab67c4240b62e99` | `6ab67c4240b62e99` |
| PR AUC | 0.9962 | 0.9984 | 0.9984 | 0.9984 |
| ROC AUC | 0.9953 | 0.9980 | 0.9980 | 0.9981 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=ea83775b3e61c4b8
```
