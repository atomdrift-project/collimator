# Confirm PASS — 2da43de64e855a82 on `filegroups/portable`

Cycle `20260527T013140-confirm-2da43de64e855a82` — 2026-05-27T01:31:40Z

PR_AUC held across 3 seeds (orig 0.9967)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `2da43de64e855a82` | `d143cbbf2cb48c24` | `d143cbbf2cb48c24` | `d143cbbf2cb48c24` |
| PR AUC | 0.9967 | 0.9961 | 0.9948 | 0.9957 |
| ROC AUC | 0.9992 | 0.9990 | 0.9988 | 0.9989 |
| Recall@3FPM | — | 0.8200 | 0.7000 | 0.8667 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=2da43de64e855a82
```
