# Confirm PASS — ba5cfc94357ff921 on `filetypes/kotlin`

Cycle `20260706T045921-confirm-ba5cfc94357ff921` — 2026-07-06T04:59:21Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ba5cfc94357ff921` | `03344a3b4c576655` | `03344a3b4c576655` | `03344a3b4c576655` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9989 | 0.9988 | 0.9990 | 0.9988 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=ba5cfc94357ff921
```
