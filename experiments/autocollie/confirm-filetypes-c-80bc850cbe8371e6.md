# Confirm PASS — 80bc850cbe8371e6 on `filetypes/c`

Cycle `20260526T034557-confirm-80bc850cbe8371e6` — 2026-05-26T03:45:57Z

PR_AUC held across 3 seeds (orig 0.9927)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `80bc850cbe8371e6` | `2f5c3d4fc322919a` | `2f5c3d4fc322919a` | `2f5c3d4fc322919a` |
| PR AUC | 0.9927 | 0.9932 | 0.9930 | 0.9930 |
| ROC AUC | 0.9962 | 0.9966 | 0.9964 | 0.9964 |
| Recall@3FPM | — | 0.7986 | 0.8125 | 0.8218 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=80bc850cbe8371e6
```
