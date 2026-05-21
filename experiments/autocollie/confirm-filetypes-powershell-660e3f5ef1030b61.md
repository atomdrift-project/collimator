# Confirm PASS — 660e3f5ef1030b61 on `filetypes/powershell`

Cycle `20260520T161210-confirm-660e3f5ef1030b61` — 2026-05-20T16:12:10Z

PR_AUC held across 3 seeds (orig 0.9986)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `660e3f5ef1030b61` | `601bb9b46810cc13` | `601bb9b46810cc13` | `601bb9b46810cc13` |
| PR AUC | 0.9986 | 0.9961 | 0.9986 | 0.9966 |
| ROC AUC | 0.9966 | 0.9911 | 0.9966 | 0.9924 |
| Recall@3FPM | — | 0.6734 | 0.8629 | 0.6694 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=660e3f5ef1030b61
```
