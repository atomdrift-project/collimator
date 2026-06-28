# Confirm PASS — 0d3757ef3cf99524 on `filegroups/config`

Cycle `20260628T152736-confirm-0d3757ef3cf99524` — 2026-06-28T15:27:36Z

PR_AUC held across 3 seeds (orig 0.9985)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0d3757ef3cf99524` | `dfa99900ae45ef74` | `dfa99900ae45ef74` | `dfa99900ae45ef74` |
| PR AUC | 0.9985 | 0.9983 | 0.9983 | 0.9983 |
| ROC AUC | 0.9984 | 0.9984 | 0.9983 | 0.9985 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0d3757ef3cf99524
```
