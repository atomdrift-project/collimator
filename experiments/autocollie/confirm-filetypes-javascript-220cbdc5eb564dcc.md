# Confirm PASS — 220cbdc5eb564dcc on `filetypes/javascript`

Cycle `20260601T203711-confirm-220cbdc5eb564dcc` — 2026-06-01T20:37:11Z

PR_AUC held across 3 seeds (orig 0.9988)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `220cbdc5eb564dcc` | `0a29176bf3ee3968` | `0a29176bf3ee3968` | `0a29176bf3ee3968` |
| PR AUC | 0.9988 | 0.9993 | 0.9993 | 0.9993 |
| ROC AUC | 0.9983 | 0.9990 | 0.9990 | 0.9990 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=220cbdc5eb564dcc
```
