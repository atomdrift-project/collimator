# Confirm PASS — e4b6c4c1a449fe6d on `filegroups/source`

Cycle `20260608T104259-confirm-e4b6c4c1a449fe6d` — 2026-06-08T10:42:59Z

PR_AUC held across 3 seeds (orig 0.9982)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e4b6c4c1a449fe6d` | `8c56283bd76abc76` | `8c56283bd76abc76` | `8c56283bd76abc76` |
| PR AUC | 0.9982 | 0.9984 | 0.9983 | 0.9983 |
| ROC AUC | 0.9975 | 0.9978 | 0.9977 | 0.9976 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e4b6c4c1a449fe6d
```
