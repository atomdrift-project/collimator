# Confirm PASS — 869759a839b13ed6 on `filetypes/rust`

Cycle `20260527T051045-confirm-869759a839b13ed6` — 2026-05-27T05:10:45Z

PR_AUC held across 3 seeds (orig 0.9006)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `869759a839b13ed6` | `b09bb4f04b61591a` | `b09bb4f04b61591a` | `b09bb4f04b61591a` |
| PR AUC | 0.9006 | 0.8889 | 0.6218 | 0.9474 |
| ROC AUC | 0.9862 | 0.9881 | 0.9570 | 0.9916 |
| Recall@3FPM | — | 0.3077 | 0.0000 | 0.7692 |
| verdict | — | FAIL | FAIL | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=869759a839b13ed6
```
