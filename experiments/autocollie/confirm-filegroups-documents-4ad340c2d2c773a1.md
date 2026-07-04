# Confirm PASS — 4ad340c2d2c773a1 on `filegroups/documents`

Cycle `20260704T080955-confirm-4ad340c2d2c773a1` — 2026-07-04T08:09:55Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `4ad340c2d2c773a1` | `f60d00cc0ede4315` | `f60d00cc0ede4315` | `f60d00cc0ede4315` |
| PR AUC | 1.0000 | 0.9999 | 0.9998 | 0.9998 |
| ROC AUC | 0.9997 | 0.9968 | 0.9949 | 0.9950 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=4ad340c2d2c773a1
```
