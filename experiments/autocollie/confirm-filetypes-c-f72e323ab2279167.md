# Confirm PASS — f72e323ab2279167 on `filetypes/c`

Cycle `20260525T035225-confirm-f72e323ab2279167` — 2026-05-25T03:52:25Z

PR_AUC held across 3 seeds (orig 0.9923)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f72e323ab2279167` | `8dc8c818e6185cf8` | `8dc8c818e6185cf8` | `8dc8c818e6185cf8` |
| PR AUC | 0.9923 | 0.9917 | 0.9916 | 0.9914 |
| ROC AUC | 0.9959 | 0.9957 | 0.9955 | 0.9955 |
| Recall@3FPM | — | 0.7662 | 0.7801 | 0.7824 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f72e323ab2279167
```
