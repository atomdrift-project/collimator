# Confirm PASS — 8bdc8fb57a82aeba on `filetypes/python`

Cycle `20260628T135704-confirm-8bdc8fb57a82aeba` — 2026-06-28T13:57:04Z

PR_AUC held across 3 seeds (orig 0.9920)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `8bdc8fb57a82aeba` | `9effa70847ad8816` | `9effa70847ad8816` | `9effa70847ad8816` |
| PR AUC | 0.9920 | 0.9892 | 0.9897 | 0.9899 |
| ROC AUC | 0.9942 | 0.9927 | 0.9932 | 0.9933 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=8bdc8fb57a82aeba
```
