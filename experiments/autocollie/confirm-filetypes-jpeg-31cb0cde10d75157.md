# Confirm PASS — 31cb0cde10d75157 on `filetypes/jpeg`

Cycle `20260602T024031-confirm-31cb0cde10d75157` — 2026-06-02T02:40:31Z

PR_AUC held across 3 seeds (orig 0.9645)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `31cb0cde10d75157` | `06e395ac6066f95e` | `06e395ac6066f95e` | `06e395ac6066f95e` |
| PR AUC | 0.9645 | 0.9824 | 0.9832 | 0.9803 |
| ROC AUC | 0.9824 | 0.9906 | 0.9910 | 0.9894 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=31cb0cde10d75157
```
