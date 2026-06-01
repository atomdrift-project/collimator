# Confirm PASS — 62b6877c5bb21700 on `filetypes/pdf`

Cycle `20260601T124853-confirm-62b6877c5bb21700` — 2026-06-01T12:48:53Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `62b6877c5bb21700` | `117fc7e5754d478f` | `117fc7e5754d478f` | `117fc7e5754d478f` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9993 | 0.9991 | 0.9981 | 0.9990 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=62b6877c5bb21700
```
