# Confirm PASS — 73fd859820a3b145 on `filetypes/javascript`

Cycle `20260606T093559-confirm-73fd859820a3b145` — 2026-06-06T09:35:59Z

PR_AUC held across 3 seeds (orig 0.9979)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `73fd859820a3b145` | `10e83ddef817a732` | `10e83ddef817a732` | `10e83ddef817a732` |
| PR AUC | 0.9979 | 0.9994 | 0.9993 | 0.9993 |
| ROC AUC | 0.9975 | 0.9991 | 0.9989 | 0.9990 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=73fd859820a3b145
```
