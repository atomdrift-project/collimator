# Confirm PASS — 2cc5a1ebfd502901 on `filetypes/gz`

Cycle `20260608T101747-confirm-2cc5a1ebfd502901` — 2026-06-08T10:17:47Z

PR_AUC held across 3 seeds (orig 0.9996)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `2cc5a1ebfd502901` | `598b8ad09815e99c` | `598b8ad09815e99c` | `598b8ad09815e99c` |
| PR AUC | 0.9996 | 0.9995 | 0.9995 | 0.9995 |
| ROC AUC | 0.9988 | 0.9987 | 0.9985 | 0.9987 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=2cc5a1ebfd502901
```
