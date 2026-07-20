# Confirm PASS — 9fb752d78a1de0b9 on `filegroups/config`

Cycle `20260715T100200-confirm-9fb752d78a1de0b9` — 2026-07-15T10:02:00Z

PR_AUC held across 3 seeds (orig 0.9976)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `9fb752d78a1de0b9` | `374fc231e3db9bad` | `374fc231e3db9bad` | `374fc231e3db9bad` |
| PR AUC | 0.9976 | 0.9981 | 0.9979 | 0.9980 |
| ROC AUC | 0.9979 | 0.9984 | 0.9984 | 0.9983 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=9fb752d78a1de0b9
```
