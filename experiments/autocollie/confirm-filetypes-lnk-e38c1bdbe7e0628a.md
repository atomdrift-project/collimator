# Confirm PASS — e38c1bdbe7e0628a on `filetypes/lnk`

Cycle `20260715T062343-confirm-e38c1bdbe7e0628a` — 2026-07-15T06:23:43Z

PR_AUC held across 3 seeds (orig 0.9978)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e38c1bdbe7e0628a` | `af4fa72b64b2c50a` | `af4fa72b64b2c50a` | `af4fa72b64b2c50a` |
| PR AUC | 0.9978 | 0.9982 | 0.9978 | 0.9985 |
| ROC AUC | 0.9894 | 0.9914 | 0.9899 | 0.9931 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e38c1bdbe7e0628a
```
