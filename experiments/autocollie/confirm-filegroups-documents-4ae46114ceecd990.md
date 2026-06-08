# Confirm PASS — 4ae46114ceecd990 on `filegroups/documents`

Cycle `20260608T120655-confirm-4ae46114ceecd990` — 2026-06-08T12:06:55Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `4ae46114ceecd990` | `af5f7976c6cfc9cd` | `af5f7976c6cfc9cd` | `af5f7976c6cfc9cd` |
| PR AUC | 0.9999 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9991 | 0.9991 | 0.9992 | 0.9991 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=4ae46114ceecd990
```
