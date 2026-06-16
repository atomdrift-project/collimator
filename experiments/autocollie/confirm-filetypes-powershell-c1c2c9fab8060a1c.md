# Confirm PASS — c1c2c9fab8060a1c on `filetypes/powershell`

Cycle `20260616T084500-confirm-c1c2c9fab8060a1c` — 2026-06-16T08:45:00Z

PR_AUC held across 3 seeds (orig 0.9993)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c1c2c9fab8060a1c` | `55e8ed90869256cc` | `55e8ed90869256cc` | `55e8ed90869256cc` |
| PR AUC | 0.9993 | 0.9992 | 0.9995 | 0.9993 |
| ROC AUC | 0.9963 | 0.9958 | 0.9975 | 0.9965 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=c1c2c9fab8060a1c
```
