# Confirm PASS — 57fbdc33d0f8d38f on `filetypes/java_class`

Cycle `20260609T051026-confirm-57fbdc33d0f8d38f` — 2026-06-09T05:10:26Z

PR_AUC held across 3 seeds (orig 0.9867)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `57fbdc33d0f8d38f` | `e38c9d62da9c7d3d` | `e38c9d62da9c7d3d` | `e38c9d62da9c7d3d` |
| PR AUC | 0.9867 | 0.9897 | 0.9908 | 0.9892 |
| ROC AUC | 0.9969 | 0.9982 | 0.9984 | 0.9981 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=57fbdc33d0f8d38f
```
