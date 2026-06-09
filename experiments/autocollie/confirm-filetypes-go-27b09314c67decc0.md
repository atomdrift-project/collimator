# Confirm PASS — 27b09314c67decc0 on `filetypes/go`

Cycle `20260608T190501-confirm-27b09314c67decc0` — 2026-06-08T19:05:01Z

PR_AUC held across 3 seeds (orig 0.9442)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `27b09314c67decc0` | `b3c616bc0fb6e577` | `b3c616bc0fb6e577` | `b3c616bc0fb6e577` |
| PR AUC | 0.9442 | 0.9487 | 0.9460 | 0.9452 |
| ROC AUC | 0.9858 | 0.9869 | 0.9852 | 0.9853 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=27b09314c67decc0
```
