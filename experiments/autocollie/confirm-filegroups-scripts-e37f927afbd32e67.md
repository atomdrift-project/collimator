# Confirm PASS — e37f927afbd32e67 on `filegroups/scripts`

Cycle `20260628T130419-confirm-e37f927afbd32e67` — 2026-06-28T13:04:19Z

PR_AUC held across 3 seeds (orig 0.9970)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e37f927afbd32e67` | `b2c82d803e6ef512` | `b2c82d803e6ef512` | `b2c82d803e6ef512` |
| PR AUC | 0.9970 | 0.9951 | 0.9952 | 0.9952 |
| ROC AUC | 0.9964 | 0.9961 | 0.9961 | 0.9962 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e37f927afbd32e67
```
