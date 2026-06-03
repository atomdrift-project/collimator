# Confirm PASS — 9766143d6df5747f on `filetypes/c`

Cycle `20260603T163510-confirm-9766143d6df5747f` — 2026-06-03T16:35:10Z

PR_AUC held across 3 seeds (orig 0.9901)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `9766143d6df5747f` | `49db159864162d12` | `49db159864162d12` | `49db159864162d12` |
| PR AUC | 0.9901 | 0.9897 | 0.9896 | 0.9895 |
| ROC AUC | 0.9961 | 0.9959 | 0.9957 | 0.9959 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=9766143d6df5747f
```
