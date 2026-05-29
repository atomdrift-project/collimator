# Confirm PASS — d79c1cbb52c60a9b on `filetypes/pe`

Cycle `20260526T104407-confirm-d79c1cbb52c60a9b` — 2026-05-26T10:44:07Z

PR_AUC held across 3 seeds (orig 0.9997)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d79c1cbb52c60a9b` | `c2042031ec133528` | `c2042031ec133528` | `c2042031ec133528` |
| PR AUC | 0.9997 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9997 | 0.9999 | 0.9999 | 0.9999 |
| Recall@3FPM | — | 0.8728 | 0.8559 | 0.8373 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d79c1cbb52c60a9b
```
