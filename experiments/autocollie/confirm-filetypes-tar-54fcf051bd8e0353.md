# Confirm PASS — 54fcf051bd8e0353 on `filetypes/tar`

Cycle `20260526T215651-confirm-54fcf051bd8e0353` — 2026-05-26T21:56:51Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `54fcf051bd8e0353` | `34210b4b1afc143f` | `34210b4b1afc143f` | `34210b4b1afc143f` |
| PR AUC | 0.9999 | 1.0000 | 0.9995 | 0.9997 |
| ROC AUC | 0.9989 | 0.9996 | 0.9956 | 0.9978 |
| Recall@3FPM | — | 0.9934 | 0.9868 | 0.9803 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=54fcf051bd8e0353
```
