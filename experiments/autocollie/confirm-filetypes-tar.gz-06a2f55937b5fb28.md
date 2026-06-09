# Confirm PASS — 06a2f55937b5fb28 on `filetypes/tar.gz`

Cycle `20260609T102312-confirm-06a2f55937b5fb28` — 2026-06-09T10:23:12Z

PR_AUC held across 3 seeds (orig 0.9991)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `06a2f55937b5fb28` | `2e0882ff8b6027c8` | `2e0882ff8b6027c8` | `2e0882ff8b6027c8` |
| PR AUC | 0.9991 | 0.9993 | 0.9992 | 0.9993 |
| ROC AUC | 0.9983 | 0.9987 | 0.9985 | 0.9987 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=06a2f55937b5fb28
```
