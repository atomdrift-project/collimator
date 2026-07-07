# Confirm PASS — fb99432f9a4e7a6d on `filegroups/portable`

Cycle `20260706T072513-confirm-fb99432f9a4e7a6d` — 2026-07-06T07:25:13Z

PR_AUC held across 3 seeds (orig 0.9909)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `fb99432f9a4e7a6d` | `7412f27e7dec6e7d` | `7412f27e7dec6e7d` | `7412f27e7dec6e7d` |
| PR AUC | 0.9909 | 0.9927 | 0.9931 | 0.9928 |
| ROC AUC | 0.9978 | 0.9981 | 0.9983 | 0.9983 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=fb99432f9a4e7a6d
```
