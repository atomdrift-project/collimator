# Confirm PASS — f41f682734dbb9cc on `filetypes/python`

Cycle `20260608T190911-confirm-f41f682734dbb9cc` — 2026-06-08T19:09:11Z

PR_AUC held across 3 seeds (orig 0.9942)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f41f682734dbb9cc` | `2444002bbdea3956` | `2444002bbdea3956` | `2444002bbdea3956` |
| PR AUC | 0.9942 | 0.9944 | 0.9946 | 0.9945 |
| ROC AUC | 0.9953 | 0.9953 | 0.9957 | 0.9956 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f41f682734dbb9cc
```
