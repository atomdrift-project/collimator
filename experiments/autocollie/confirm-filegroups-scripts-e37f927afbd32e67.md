# Confirm PASS — e37f927afbd32e67 on `filegroups/scripts`

Cycle `20260608T102559-confirm-e37f927afbd32e67` — 2026-06-08T10:25:59Z

PR_AUC held across 3 seeds (orig 0.9970)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e37f927afbd32e67` | `bcae0f6984fea346` | `bcae0f6984fea346` | `bcae0f6984fea346` |
| PR AUC | 0.9970 | 0.9986 | 0.9985 | 0.9986 |
| ROC AUC | 0.9964 | 0.9982 | 0.9982 | 0.9982 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e37f927afbd32e67
```
