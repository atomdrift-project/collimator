# Confirm PASS — b6fa08ca50a9ac54 on `filetypes/pe`

Cycle `20260704T121750-confirm-b6fa08ca50a9ac54` — 2026-07-04T12:17:50Z

PR_AUC held across 3 seeds (orig 0.9997)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b6fa08ca50a9ac54` | `0f16e9d9ad9c6710` | `0f16e9d9ad9c6710` | `0f16e9d9ad9c6710` |
| PR AUC | 0.9997 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9997 | 0.9997 | 0.9997 | 0.9997 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b6fa08ca50a9ac54
```
