# Confirm PASS — 7b4e830487cd47b3 on `filetypes/makefile`

Cycle `20260527T053549-confirm-7b4e830487cd47b3` — 2026-05-27T05:35:49Z

PR_AUC held across 3 seeds (orig 0.2084)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `7b4e830487cd47b3` | `c1ec303e156eed55` | `c1ec303e156eed55` | `c1ec303e156eed55` |
| PR AUC | 0.2084 | 0.9313 | 0.7961 | 0.9126 |
| ROC AUC | 0.9078 | 0.9991 | 0.9989 | 0.9994 |
| Recall@3FPM | — | 0.6667 | 0.1429 | 0.3333 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=7b4e830487cd47b3
```
