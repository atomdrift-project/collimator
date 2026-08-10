# Confirm PASS — 0b8acdcee97d806b on `filetypes/batch`

Cycle `20260804T210937-confirm-0b8acdcee97d806b` — 2026-08-04T21:09:37Z

PR_AUC held across 3 seeds (orig 0.9982)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0b8acdcee97d806b` | `f3001f006573adf1` | `f3001f006573adf1` | `f3001f006573adf1` |
| PR AUC | 0.9982 | 0.9993 | 0.9986 | 0.9987 |
| ROC AUC | 0.9868 | 0.9899 | 0.9792 | 0.9804 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0b8acdcee97d806b
```
