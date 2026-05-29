# Confirm PASS — 825216f29184cdc5 on `filetypes/text`

Cycle `20260527T015233-confirm-825216f29184cdc5` — 2026-05-27T01:52:33Z

PR_AUC held across 3 seeds (orig 0.9703)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `825216f29184cdc5` | `4ffea8c2e1af9c57` | `4ffea8c2e1af9c57` | `4ffea8c2e1af9c57` |
| PR AUC | 0.9703 | 0.9595 | 0.9740 | 0.9624 |
| ROC AUC | 0.9851 | 0.9835 | 0.9881 | 0.9799 |
| Recall@3FPM | — | 0.6190 | 0.8095 | 0.8095 |
| verdict | — | FAIL | PASS | FAIL |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=825216f29184cdc5
```
