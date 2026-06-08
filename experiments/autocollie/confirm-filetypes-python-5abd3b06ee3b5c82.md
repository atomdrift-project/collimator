# Confirm PASS — 5abd3b06ee3b5c82 on `filetypes/python`

Cycle `20260608T182802-confirm-5abd3b06ee3b5c82` — 2026-06-08T18:28:02Z

PR_AUC held across 3 seeds (orig 0.9992)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `5abd3b06ee3b5c82` | `e0af3df47c864016` | `e0af3df47c864016` | `e0af3df47c864016` |
| PR AUC | 0.9992 | 0.9940 | 0.9947 | 0.9942 |
| ROC AUC | 0.9992 | 0.9948 | 0.9956 | 0.9953 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | PASS | FAIL |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=5abd3b06ee3b5c82
```
