# Confirm PASS — 8872f0c9ad7c1565 on `filegroups/media`

Cycle `20260713T011353-confirm-8872f0c9ad7c1565` — 2026-07-13T01:13:53Z

PR_AUC held across 3 seeds (orig 0.9863)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `8872f0c9ad7c1565` | `90944f5aa6710c78` | `90944f5aa6710c78` | `90944f5aa6710c78` |
| PR AUC | 0.9863 | 0.9871 | 0.9875 | 0.9903 |
| ROC AUC | 0.9784 | 0.9776 | 0.9805 | 0.9860 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=8872f0c9ad7c1565
```
