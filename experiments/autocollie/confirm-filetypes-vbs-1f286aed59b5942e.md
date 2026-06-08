# Confirm PASS — 1f286aed59b5942e on `filetypes/vbs`

Cycle `20260608T160703-confirm-1f286aed59b5942e` — 2026-06-08T16:07:03Z

PR_AUC held across 3 seeds (orig 0.9976)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `1f286aed59b5942e` | `6f86087bbbadb07e` | `6f86087bbbadb07e` | `6f86087bbbadb07e` |
| PR AUC | 0.9976 | 0.9976 | 0.9973 | 0.9974 |
| ROC AUC | 0.9920 | 0.9919 | 0.9908 | 0.9913 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=1f286aed59b5942e
```
