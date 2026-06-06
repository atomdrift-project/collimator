# Confirm PASS — 236c6a54f5d870b6 on `filegroups/source`

Cycle `20260606T094001-confirm-236c6a54f5d870b6` — 2026-06-06T09:40:01Z

PR_AUC held across 3 seeds (orig 0.9987)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `236c6a54f5d870b6` | `e4fad6b170282450` | `e4fad6b170282450` | `e4fad6b170282450` |
| PR AUC | 0.9987 | 0.9988 | 0.9987 | 0.9988 |
| ROC AUC | 0.9982 | 0.9983 | 0.9982 | 0.9983 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=236c6a54f5d870b6
```
