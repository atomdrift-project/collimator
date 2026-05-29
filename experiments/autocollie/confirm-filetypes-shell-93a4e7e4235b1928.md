# Confirm PASS — 93a4e7e4235b1928 on `filetypes/shell`

Cycle `20260527T010520-confirm-93a4e7e4235b1928` — 2026-05-27T01:05:20Z

PR_AUC held across 3 seeds (orig 0.9986)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `93a4e7e4235b1928` | `b2f9c8bedfdd90ad` | `b2f9c8bedfdd90ad` | `b2f9c8bedfdd90ad` |
| PR AUC | 0.9986 | 0.9969 | 0.9970 | 0.9970 |
| ROC AUC | 0.9996 | 0.9979 | 0.9979 | 0.9979 |
| Recall@3FPM | — | 0.8734 | 0.8305 | 0.8455 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=93a4e7e4235b1928
```
