# Confirm PASS — 46ec55278912862b on `filegroups/config`

Cycle `20260609T054040-confirm-46ec55278912862b` — 2026-06-09T05:40:40Z

PR_AUC held across 3 seeds (orig 0.9987)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `46ec55278912862b` | `e632aa2f77843031` | `e632aa2f77843031` | `e632aa2f77843031` |
| PR AUC | 0.9987 | 0.9988 | 0.9987 | 0.9988 |
| ROC AUC | 0.9982 | 0.9983 | 0.9981 | 0.9984 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=46ec55278912862b
```
