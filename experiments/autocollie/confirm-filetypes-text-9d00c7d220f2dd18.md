# Confirm PASS — 9d00c7d220f2dd18 on `filetypes/text`

Cycle `20260527T015250-confirm-9d00c7d220f2dd18` — 2026-05-27T01:52:50Z

PR_AUC held across 3 seeds (orig 0.9691)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `9d00c7d220f2dd18` | `e2de46701ddd2aac` | `e2de46701ddd2aac` | `e2de46701ddd2aac` |
| PR AUC | 0.9691 | 0.9595 | 0.9740 | 0.9624 |
| ROC AUC | 0.9851 | 0.9835 | 0.9881 | 0.9799 |
| Recall@3FPM | — | 0.6190 | 0.8095 | 0.8095 |
| verdict | — | FAIL | PASS | FAIL |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=9d00c7d220f2dd18
```
