# Confirm PASS — a2fe1f641a4aa12d on `filetypes/java`

Cycle `20260613T024010-confirm-a2fe1f641a4aa12d` — 2026-06-13T02:40:10Z

PR_AUC held across 3 seeds (orig 0.9581)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a2fe1f641a4aa12d` | `cf47478680c84ac1` | `cf47478680c84ac1` | `cf47478680c84ac1` |
| PR AUC | 0.9581 | 0.9721 | 0.9681 | 0.9637 |
| ROC AUC | 0.9594 | 0.9683 | 0.9656 | 0.9644 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a2fe1f641a4aa12d
```
