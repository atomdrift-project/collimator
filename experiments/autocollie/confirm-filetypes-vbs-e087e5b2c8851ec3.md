# Confirm PASS — e087e5b2c8851ec3 on `filetypes/vbs`

Cycle `20260613T232658-confirm-e087e5b2c8851ec3` — 2026-06-13T23:26:58Z

PR_AUC held across 3 seeds (orig 0.9967)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e087e5b2c8851ec3` | `fee76c2cdc8daf3a` | `fee76c2cdc8daf3a` | `fee76c2cdc8daf3a` |
| PR AUC | 0.9967 | 0.9973 | 0.9975 | 0.9970 |
| ROC AUC | 0.9887 | 0.9902 | 0.9910 | 0.9891 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e087e5b2c8851ec3
```
