# Confirm PASS — 4a850d382b1d464f on `filetypes/ole`

Cycle `20260608T111932-confirm-4a850d382b1d464f` — 2026-06-08T11:19:32Z

PR_AUC held across 3 seeds (orig 0.9966)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `4a850d382b1d464f` | `63d97b70bb8ff0af` | `63d97b70bb8ff0af` | `63d97b70bb8ff0af` |
| PR AUC | 0.9966 | 0.9973 | 0.9965 | 0.9973 |
| ROC AUC | 0.9960 | 0.9966 | 0.9958 | 0.9966 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=4a850d382b1d464f
```
