# Confirm PASS — b44dfc52f25c20ad on `filegroups/native`

Cycle `20260615T065516-confirm-b44dfc52f25c20ad` — 2026-06-15T06:55:16Z

PR_AUC held across 3 seeds (orig 0.9994)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b44dfc52f25c20ad` | `e8d578721e485c2c` | `e8d578721e485c2c` | `e8d578721e485c2c` |
| PR AUC | 0.9994 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9994 | 0.9999 | 0.9999 | 0.9999 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b44dfc52f25c20ad
```
