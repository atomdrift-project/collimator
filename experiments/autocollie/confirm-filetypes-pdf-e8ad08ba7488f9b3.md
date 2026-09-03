# Confirm PASS — e8ad08ba7488f9b3 on `filetypes/pdf`

Cycle `20260825T223747-confirm-e8ad08ba7488f9b3` — 2026-08-25T22:37:47Z

PR_AUC held across 3 seeds (orig 0.9982)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e8ad08ba7488f9b3` | `758474dee5bb8346` | `758474dee5bb8346` | `758474dee5bb8346` |
| PR AUC | 0.9982 | 0.9991 | 0.9992 | 0.9981 |
| ROC AUC | 0.9949 | 0.9944 | 0.9950 | 0.9884 |
| Recall@L50 | — | 0.7693 | 0.8362 | 0.7601 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e8ad08ba7488f9b3
```
