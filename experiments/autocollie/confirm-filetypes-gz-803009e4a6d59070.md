# Confirm PASS — 803009e4a6d59070 on `filetypes/gz`

Cycle `20260526T205228-confirm-803009e4a6d59070` — 2026-05-26T20:52:28Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `803009e4a6d59070` | `e622e9c3b2e47f2e` | `e622e9c3b2e47f2e` | `e622e9c3b2e47f2e` |
| PR AUC | 1.0000 | 0.9984 | 0.9986 | 0.9986 |
| ROC AUC | 1.0000 | 0.9979 | 0.9981 | 0.9981 |
| Recall@3FPM | — | 0.9913 | 0.9913 | 0.9913 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=803009e4a6d59070
```
