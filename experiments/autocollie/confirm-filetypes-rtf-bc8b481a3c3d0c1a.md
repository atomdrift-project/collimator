# Confirm PASS — bc8b481a3c3d0c1a on `filetypes/rtf`

Cycle `20260608T052542-confirm-bc8b481a3c3d0c1a` — 2026-06-08T05:25:42Z

PR_AUC held across 3 seeds (orig 0.9996)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `bc8b481a3c3d0c1a` | `de31ead74d91bf8f` | `de31ead74d91bf8f` | `de31ead74d91bf8f` |
| PR AUC | 0.9996 | 0.9996 | 0.9986 | 0.9986 |
| ROC AUC | 0.9968 | 0.9965 | 0.9918 | 0.9917 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=bc8b481a3c3d0c1a
```
