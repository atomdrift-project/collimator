# Confirm PASS — 8be8ef2448af9937 on `filegroups/documents`

Cycle `20260526T220502-confirm-8be8ef2448af9937` — 2026-05-26T22:05:02Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `8be8ef2448af9937` | `a817ae4b9e792f16` | `a817ae4b9e792f16` | `a817ae4b9e792f16` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9991 | 0.9997 | 0.9997 | 0.9998 |
| Recall@3FPM | — | 0.9717 | 0.9851 | 0.9811 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=8be8ef2448af9937
```
