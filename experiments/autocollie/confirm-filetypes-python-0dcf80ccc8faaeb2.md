# Confirm PASS — 0dcf80ccc8faaeb2 on `filetypes/python`

Cycle `20260628T141220-confirm-0dcf80ccc8faaeb2` — 2026-06-28T14:12:20Z

PR_AUC held across 3 seeds (orig 0.9884)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0dcf80ccc8faaeb2` | `9effa70847ad8816` | `9effa70847ad8816` | `9effa70847ad8816` |
| PR AUC | 0.9884 | 0.9892 | 0.9897 | 0.9899 |
| ROC AUC | 0.9923 | 0.9927 | 0.9932 | 0.9933 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0dcf80ccc8faaeb2
```
