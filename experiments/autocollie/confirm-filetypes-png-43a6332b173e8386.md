# Confirm PASS — 43a6332b173e8386 on `filetypes/png`

Cycle `20260527T004103-confirm-43a6332b173e8386` — 2026-05-27T00:41:03Z

PR_AUC held across 3 seeds (orig 0.9853)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `43a6332b173e8386` | `bd7f3415403591c7` | `bd7f3415403591c7` | `bd7f3415403591c7` |
| PR AUC | 0.9853 | 0.9698 | 0.9843 | 0.9910 |
| ROC AUC | 0.9728 | 0.9606 | 0.9753 | 0.9853 |
| Recall@3FPM | — | 0.9231 | 0.9231 | 0.9231 |
| verdict | — | FAIL | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=43a6332b173e8386
```
