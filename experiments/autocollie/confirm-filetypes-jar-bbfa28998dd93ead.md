# Confirm PASS — bbfa28998dd93ead on `filetypes/jar`

Cycle `20260615T064727-confirm-bbfa28998dd93ead` — 2026-06-15T06:47:27Z

PR_AUC held across 3 seeds (orig 0.9860)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `bbfa28998dd93ead` | `14779a2b9562d0af` | `14779a2b9562d0af` | `14779a2b9562d0af` |
| PR AUC | 0.9860 | 0.9878 | 0.9880 | 0.9936 |
| ROC AUC | 0.9700 | 0.9742 | 0.9744 | 0.9868 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=bbfa28998dd93ead
```
