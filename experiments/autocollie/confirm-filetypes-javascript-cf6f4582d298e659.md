# Confirm PASS — cf6f4582d298e659 on `filetypes/javascript`

Cycle `20260704T091955-confirm-cf6f4582d298e659` — 2026-07-04T09:19:55Z

PR_AUC held across 3 seeds (orig 0.9994)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `cf6f4582d298e659` | `13b040e007800d32` | `13b040e007800d32` | `13b040e007800d32` |
| PR AUC | 0.9994 | 0.9989 | 0.9988 | 0.9988 |
| ROC AUC | 0.9990 | 0.9987 | 0.9987 | 0.9987 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=cf6f4582d298e659
```
