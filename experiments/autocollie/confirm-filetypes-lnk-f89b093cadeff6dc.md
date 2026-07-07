# Confirm PASS — f89b093cadeff6dc on `filetypes/lnk`

Cycle `20260706T081113-confirm-f89b093cadeff6dc` — 2026-07-06T08:11:13Z

PR_AUC held across 3 seeds (orig 0.9974)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f89b093cadeff6dc` | `2a8c8edbcf62a323` | `2a8c8edbcf62a323` | `2a8c8edbcf62a323` |
| PR AUC | 0.9974 | 0.9977 | 0.9981 | 0.9981 |
| ROC AUC | 0.9876 | 0.9891 | 0.9910 | 0.9907 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f89b093cadeff6dc
```
