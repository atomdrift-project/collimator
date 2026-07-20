# Confirm PASS — 0ad91806d2385c44 on `filetypes/csharp`

Cycle `20260709T121031-confirm-0ad91806d2385c44` — 2026-07-09T12:10:31Z

PR_AUC held across 3 seeds (orig 0.9892)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0ad91806d2385c44` | `debd1e7f8941f433` | `debd1e7f8941f433` | `debd1e7f8941f433` |
| PR AUC | 0.9892 | 0.9896 | 0.9882 | 0.9880 |
| ROC AUC | 0.9968 | 0.9971 | 0.9964 | 0.9964 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0ad91806d2385c44
```
