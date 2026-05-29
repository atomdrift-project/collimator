# Confirm PASS — 02fea278b325858d on `filetypes/jar`

Cycle `20260526T231940-confirm-02fea278b325858d` — 2026-05-26T23:19:40Z

PR_AUC held across 3 seeds (orig 0.9933)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `02fea278b325858d` | `81413a8b02020e8b` | `81413a8b02020e8b` | `81413a8b02020e8b` |
| PR AUC | 0.9933 | 0.9985 | 0.9983 | 0.9988 |
| ROC AUC | 0.9966 | 0.9989 | 0.9988 | 0.9991 |
| Recall@3FPM | — | 0.8958 | 0.9062 | 0.9427 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=02fea278b325858d
```
