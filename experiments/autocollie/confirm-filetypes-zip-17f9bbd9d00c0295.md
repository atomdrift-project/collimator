# Confirm PASS — 17f9bbd9d00c0295 on `filetypes/zip`

Cycle `20260616T103124-confirm-17f9bbd9d00c0295` — 2026-06-16T10:31:24Z

PR_AUC held across 3 seeds (orig 0.9997)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `17f9bbd9d00c0295` | `4d51eb3e6190c01d` | `4d51eb3e6190c01d` | `4d51eb3e6190c01d` |
| PR AUC | 0.9997 | 0.9997 | 0.9996 | 0.9996 |
| ROC AUC | 0.9980 | 0.9979 | 0.9975 | 0.9977 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=17f9bbd9d00c0295
```
