# Confirm PASS — 74e0baa1436476df on `filegroups/documents`

Cycle `20260601T134541-confirm-74e0baa1436476df` — 2026-06-01T13:45:41Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `74e0baa1436476df` | `ba2ab7cd8020fcac` | `ba2ab7cd8020fcac` | `ba2ab7cd8020fcac` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9998 | 0.9992 | 0.9992 | 0.9992 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=74e0baa1436476df
```
