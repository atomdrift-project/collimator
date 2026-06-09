# Confirm PASS — e087e5b2c8851ec3 on `filetypes/vbs`

Cycle `20260609T112643-confirm-e087e5b2c8851ec3` — 2026-06-09T11:26:43Z

PR_AUC held across 3 seeds (orig 0.9967)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e087e5b2c8851ec3` | `9d67d840a5bee0e2` | `9d67d840a5bee0e2` | `9d67d840a5bee0e2` |
| PR AUC | 0.9967 | 0.9967 | 0.9970 | 0.9969 |
| ROC AUC | 0.9887 | 0.9884 | 0.9897 | 0.9892 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e087e5b2c8851ec3
```
