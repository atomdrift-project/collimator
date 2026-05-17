# Confirm PASS — ab0e69c47bbe6810 on `filetypes/xml`

Cycle `20260514T151544-confirm-ab0e69c47bbe6810` — 2026-05-14T15:15:44Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ab0e69c47bbe6810` | `f4ab8408cd277f79` | `f4ab8408cd277f79` | `f4ab8408cd277f79` |
| PR AUC | 1.0000 | 1.0000 | 0.9967 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 0.9996 | 1.0000 |
| Recall@3FPM | — | 1.0000 | 0.9412 | 1.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=ab0e69c47bbe6810
```
