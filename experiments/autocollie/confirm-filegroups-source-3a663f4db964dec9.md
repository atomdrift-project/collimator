# Confirm PASS — 3a663f4db964dec9 on `filegroups/source`

Cycle `20260601T144047-confirm-3a663f4db964dec9` — 2026-06-01T14:40:47Z

PR_AUC held across 3 seeds (orig 0.9991)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3a663f4db964dec9` | `d26f630cb0296c50` | `d26f630cb0296c50` | `d26f630cb0296c50` |
| PR AUC | 0.9991 | 0.9989 | 0.9989 | 0.9988 |
| ROC AUC | 0.9983 | 0.9981 | 0.9982 | 0.9979 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3a663f4db964dec9
```
