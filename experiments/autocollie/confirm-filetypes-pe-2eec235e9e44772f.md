# Confirm PASS — 2eec235e9e44772f on `filetypes/pe`

Cycle `20260601T210143-confirm-2eec235e9e44772f` — 2026-06-01T21:01:43Z

PR_AUC held across 3 seeds (orig 0.9997)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `2eec235e9e44772f` | `d622cdc124b79c3a` | `d622cdc124b79c3a` | `d622cdc124b79c3a` |
| PR AUC | 0.9997 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9997 | 0.9999 | 0.9999 | 0.9999 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=2eec235e9e44772f
```
