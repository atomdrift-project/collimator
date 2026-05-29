# Confirm PASS — bd0d38192e5844aa on `filetypes/shell`

Cycle `20260527T004455-confirm-bd0d38192e5844aa` — 2026-05-27T00:44:55Z

PR_AUC held across 3 seeds (orig 0.9984)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `bd0d38192e5844aa` | `2a83accac78675ab` | `2a83accac78675ab` | `2a83accac78675ab` |
| PR AUC | 0.9984 | 0.9972 | 0.9973 | 0.9973 |
| ROC AUC | 0.9995 | 0.9980 | 0.9982 | 0.9981 |
| Recall@3FPM | — | 0.8863 | 0.8552 | 0.8906 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=bd0d38192e5844aa
```
