# Confirm PASS — a8ae761c1d5b7545 on `filetypes/zip`

Cycle `20260524T200738-confirm-a8ae761c1d5b7545` — 2026-05-24T20:07:38Z

PR_AUC held across 3 seeds (orig 0.9998)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a8ae761c1d5b7545` | `f5b8af3e2cec792b` | `f5b8af3e2cec792b` | `f5b8af3e2cec792b` |
| PR AUC | 0.9998 | 0.9997 | 0.9998 | 0.9997 |
| ROC AUC | 0.9960 | 0.9958 | 0.9960 | 0.9954 |
| Recall@3FPM | — | 0.6825 | 0.7086 | 0.6551 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a8ae761c1d5b7545
```
