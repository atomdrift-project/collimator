# Confirm PASS — 3777e577d3f30f3d on `filetypes/vbs`

Cycle `20260603T163444-confirm-3777e577d3f30f3d` — 2026-06-03T16:34:44Z

PR_AUC held across 3 seeds (orig 0.9995)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3777e577d3f30f3d` | `c7508b5ef823ae90` | `c7508b5ef823ae90` | `c7508b5ef823ae90` |
| PR AUC | 0.9995 | 0.9980 | 0.9997 | 0.9977 |
| ROC AUC | 0.9898 | 0.9655 | 0.9935 | 0.9583 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3777e577d3f30f3d
```
