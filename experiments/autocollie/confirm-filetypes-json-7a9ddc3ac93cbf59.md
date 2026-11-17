# Confirm PASS — 7a9ddc3ac93cbf59 on `filetypes/json`

Cycle `20261112T122317-confirm-7a9ddc3ac93cbf59` — 2026-11-12T12:23:17Z

averaged 3-seed ensemble PR_AUC held: 0.9635 -> 0.9752; individual seeds may be noisy

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `7a9ddc3ac93cbf59` | `8bae31b0fa032ef6` | `8bae31b0fa032ef6` | `8bae31b0fa032ef6` |
| PR AUC | 0.9635 | 0.9722 | 0.9765 | 0.9743 |
| ROC AUC | 0.9966 | 0.9983 | 0.9976 | 0.9975 |
| Recall@L50 | — | 0.3559 | 0.4237 | 0.5198 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=7a9ddc3ac93cbf59
```
