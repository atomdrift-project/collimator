# Confirm PASS — a9138b83a6eb3968 on `filetypes/package.json`

Cycle `20260723T050540-confirm-a9138b83a6eb3968` — 2026-07-23T05:05:40Z

PR_AUC held across 3 seeds (orig 0.9982)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a9138b83a6eb3968` | `8b37986a14f80ede` | `8b37986a14f80ede` | `8b37986a14f80ede` |
| PR AUC | 0.9982 | 0.9980 | 0.9979 | 0.9979 |
| ROC AUC | 0.9984 | 0.9981 | 0.9981 | 0.9980 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a9138b83a6eb3968
```
