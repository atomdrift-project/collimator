# Confirm PASS — 3f996ee5a5a631b3 on `filetypes/gz`

Cycle `20260515T081610-confirm-3f996ee5a5a631b3` — 2026-05-15T08:16:10Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3f996ee5a5a631b3` | `f18dd465af6dc61f` | `f18dd465af6dc61f` | `f18dd465af6dc61f` |
| PR AUC | 0.9999 | 0.9999 | 0.9999 | 0.9997 |
| ROC AUC | 0.9998 | 0.9998 | 0.9998 | 0.9992 |
| Recall@3FPM | — | 0.9907 | 0.9907 | 0.9907 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3f996ee5a5a631b3
```
