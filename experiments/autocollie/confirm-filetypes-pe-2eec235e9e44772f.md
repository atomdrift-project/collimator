# Confirm PASS — 2eec235e9e44772f on `filetypes/pe`

Cycle `20260704T105353-confirm-2eec235e9e44772f` — 2026-07-04T10:53:53Z

PR_AUC held across 3 seeds (orig 0.9997)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `2eec235e9e44772f` | `36bb00c606ccf012` | `36bb00c606ccf012` | `36bb00c606ccf012` |
| PR AUC | 0.9997 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9997 | 0.9997 | 0.9997 | 0.9997 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=2eec235e9e44772f
```
