# Confirm PASS — 0fb64f9d99dce8e1 on `filetypes/python`

Cycle `20260602T011528-confirm-0fb64f9d99dce8e1` — 2026-06-02T01:15:28Z

PR_AUC held across 3 seeds (orig 0.9990)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0fb64f9d99dce8e1` | `d0c61506a50992a8` | `d0c61506a50992a8` | `d0c61506a50992a8` |
| PR AUC | 0.9990 | 0.9972 | 0.9975 | 0.9973 |
| ROC AUC | 0.9991 | 0.9979 | 0.9982 | 0.9980 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0fb64f9d99dce8e1
```
