# Confirm PASS — 47a53ca04817cb3f on `filegroups/documents`

Cycle `20260522T165429-confirm-47a53ca04817cb3f` — 2026-05-22T16:54:29Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `47a53ca04817cb3f` | `2da06d3766024655` | `2da06d3766024655` | `2da06d3766024655` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9986 | 0.9978 | 0.9971 | 0.9980 |
| Recall@3FPM | — | 0.9528 | 0.9364 | 0.9667 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=47a53ca04817cb3f
```
