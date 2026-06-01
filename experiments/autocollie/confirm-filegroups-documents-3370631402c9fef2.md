# Confirm PASS — 3370631402c9fef2 on `filegroups/documents`

Cycle `20260601T132412-confirm-3370631402c9fef2` — 2026-06-01T13:24:12Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3370631402c9fef2` | `00650271b0f5884a` | `00650271b0f5884a` | `00650271b0f5884a` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9997 | 0.9993 | 0.9993 | 0.9993 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3370631402c9fef2
```
