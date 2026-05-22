# Confirm PASS — 3f653acb0360208e on `filegroups/source`

Cycle `20260522T173521-confirm-3f653acb0360208e` — 2026-05-22T17:35:21Z

PR_AUC held across 3 seeds (orig 0.9988)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3f653acb0360208e` | `1eef94903660b7de` | `1eef94903660b7de` | `1eef94903660b7de` |
| PR AUC | 0.9988 | 0.9987 | 0.9987 | 0.9987 |
| ROC AUC | 0.9981 | 0.9979 | 0.9980 | 0.9980 |
| Recall@3FPM | — | 0.9079 | 0.9068 | 0.9137 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3f653acb0360208e
```
