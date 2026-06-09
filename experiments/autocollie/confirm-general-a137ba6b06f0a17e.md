# Confirm PASS — a137ba6b06f0a17e on `general`

Cycle `20260609T033348-confirm-a137ba6b06f0a17e` — 2026-06-09T03:33:48Z

PR_AUC held across 3 seeds (orig 0.9981)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a137ba6b06f0a17e` | `bec3854af4755c7a` | `bec3854af4755c7a` | `bec3854af4755c7a` |
| PR AUC | 0.9981 | 0.9998 | 0.9998 | 0.9998 |
| ROC AUC | 0.9979 | 0.9994 | 0.9993 | 0.9994 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a137ba6b06f0a17e
```
