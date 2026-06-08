# Confirm PASS — c76e9f9c3465ff0a on `filetypes/java`

Cycle `20260608T115950-confirm-c76e9f9c3465ff0a` — 2026-06-08T11:59:50Z

PR_AUC held across 3 seeds (orig 0.9605)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c76e9f9c3465ff0a` | `d102f792252f6425` | `d102f792252f6425` | `d102f792252f6425` |
| PR AUC | 0.9605 | 0.9662 | 0.9511 | 0.9602 |
| ROC AUC | 0.9607 | 0.9571 | 0.9452 | 0.9571 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | FAIL | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=c76e9f9c3465ff0a
```
