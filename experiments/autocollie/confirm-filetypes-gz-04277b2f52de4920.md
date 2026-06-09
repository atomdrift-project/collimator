# Confirm PASS — 04277b2f52de4920 on `filetypes/gz`

Cycle `20260609T105036-confirm-04277b2f52de4920` — 2026-06-09T10:50:36Z

PR_AUC held across 3 seeds (orig 0.9997)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `04277b2f52de4920` | `0ecb65edb671c92e` | `0ecb65edb671c92e` | `0ecb65edb671c92e` |
| PR AUC | 0.9997 | 0.9997 | 0.9997 | 0.9997 |
| ROC AUC | 0.9992 | 0.9991 | 0.9992 | 0.9991 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=04277b2f52de4920
```
