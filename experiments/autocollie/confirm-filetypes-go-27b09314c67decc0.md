# Confirm PASS — 27b09314c67decc0 on `filetypes/go`

Cycle `20260614T220453-confirm-27b09314c67decc0` — 2026-06-14T22:04:53Z

PR_AUC held across 3 seeds (orig 0.9442)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `27b09314c67decc0` | `f1b70725f49946d2` | `f1b70725f49946d2` | `f1b70725f49946d2` |
| PR AUC | 0.9442 | 0.9440 | 0.9339 | 0.9410 |
| ROC AUC | 0.9858 | 0.9863 | 0.9834 | 0.9841 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | FAIL | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=27b09314c67decc0
```
