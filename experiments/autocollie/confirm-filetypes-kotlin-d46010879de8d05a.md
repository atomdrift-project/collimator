# Confirm PASS — d46010879de8d05a on `filetypes/kotlin`

Cycle `20260603T155716-confirm-d46010879de8d05a` — 2026-06-03T15:57:16Z

PR_AUC held across 3 seeds (orig 0.9961)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d46010879de8d05a` | `0084f0c35548775f` | `0084f0c35548775f` | `0084f0c35548775f` |
| PR AUC | 0.9961 | 0.9991 | 0.9965 | 0.9996 |
| ROC AUC | 0.8652 | 0.9625 | 0.8764 | 0.9756 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d46010879de8d05a
```
