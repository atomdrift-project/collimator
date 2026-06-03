# Confirm PASS — 581b030ce42960a8 on `filetypes/java_class`

Cycle `20260603T155330-confirm-581b030ce42960a8` — 2026-06-03T15:53:30Z

PR_AUC held across 3 seeds (orig 0.9970)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `581b030ce42960a8` | `09dbc099bd16c40d` | `09dbc099bd16c40d` | `09dbc099bd16c40d` |
| PR AUC | 0.9970 | 0.9947 | 0.9944 | 0.9940 |
| ROC AUC | 0.9995 | 0.9987 | 0.9992 | 0.9985 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=581b030ce42960a8
```
