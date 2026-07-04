# Confirm PASS — cd8a67b3691cc6ee on `filetypes/vbs`

Cycle `20260704T132108-confirm-cd8a67b3691cc6ee` — 2026-07-04T13:21:08Z

PR_AUC held across 3 seeds (orig 0.9989)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `cd8a67b3691cc6ee` | `41a04980bd128f2e` | `41a04980bd128f2e` | `41a04980bd128f2e` |
| PR AUC | 0.9989 | 0.9990 | 0.9989 | 0.9989 |
| ROC AUC | 0.9960 | 0.9966 | 0.9961 | 0.9963 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=cd8a67b3691cc6ee
```
