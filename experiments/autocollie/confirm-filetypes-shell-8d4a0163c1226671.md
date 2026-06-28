# Confirm PASS — 8d4a0163c1226671 on `filetypes/shell`

Cycle `20260628T123311-confirm-8d4a0163c1226671` — 2026-06-28T12:33:11Z

PR_AUC held across 3 seeds (orig 0.9959)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `8d4a0163c1226671` | `26d8fc42f49d25ed` | `26d8fc42f49d25ed` | `26d8fc42f49d25ed` |
| PR AUC | 0.9959 | 0.9948 | 0.9945 | 0.9950 |
| ROC AUC | 0.9968 | 0.9960 | 0.9958 | 0.9961 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=8d4a0163c1226671
```
