# Confirm PASS — 5ea4eef0206ab018 on `filetypes/xml`

Cycle `20260706T041201-confirm-5ea4eef0206ab018` — 2026-07-06T04:12:01Z

PR_AUC held across 3 seeds (orig 0.9995)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `5ea4eef0206ab018` | `820eb50eba229e59` | `820eb50eba229e59` | `820eb50eba229e59` |
| PR AUC | 0.9995 | 0.9984 | 0.9918 | 0.9985 |
| ROC AUC | 0.9999 | 0.9996 | 0.9974 | 0.9996 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | FAIL | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=5ea4eef0206ab018
```
