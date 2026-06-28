# Confirm PASS — fa8d5bccea9a86b0 on `filetypes/powershell`

Cycle `20260628T110111-confirm-fa8d5bccea9a86b0` — 2026-06-28T11:01:11Z

PR_AUC held across 3 seeds (orig 0.9990)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `fa8d5bccea9a86b0` | `90f4d6ac6a0c06aa` | `90f4d6ac6a0c06aa` | `90f4d6ac6a0c06aa` |
| PR AUC | 0.9990 | 0.9984 | 0.9988 | 0.9984 |
| ROC AUC | 0.9951 | 0.9935 | 0.9951 | 0.9936 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=fa8d5bccea9a86b0
```
