# Confirm PASS — bfe35702994cc387 on `filetypes/kotlin`

Cycle `20260704T151345-confirm-bfe35702994cc387` — 2026-07-04T15:13:45Z

PR_AUC held across 3 seeds (orig 0.9773)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `bfe35702994cc387` | `15b5f8b4b1b9a6a3` | `15b5f8b4b1b9a6a3` | `15b5f8b4b1b9a6a3` |
| PR AUC | 0.9773 | 0.9799 | 0.9729 | 0.9812 |
| ROC AUC | 0.9835 | 0.9870 | 0.9834 | 0.9881 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=bfe35702994cc387
```
