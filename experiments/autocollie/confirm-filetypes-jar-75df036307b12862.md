# Confirm PASS — 75df036307b12862 on `filetypes/jar`

Cycle `20260526T231558-confirm-75df036307b12862` — 2026-05-26T23:15:58Z

PR_AUC held across 3 seeds (orig 0.9983)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `75df036307b12862` | `29448a58ecc1da3a` | `29448a58ecc1da3a` | `29448a58ecc1da3a` |
| PR AUC | 0.9983 | 0.9975 | 0.9988 | 0.9985 |
| ROC AUC | 0.9966 | 0.9949 | 0.9978 | 0.9974 |
| Recall@3FPM | — | 0.8807 | 0.8920 | 0.8580 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=75df036307b12862
```
