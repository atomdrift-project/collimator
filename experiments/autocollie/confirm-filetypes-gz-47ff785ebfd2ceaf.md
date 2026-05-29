# Confirm PASS — 47ff785ebfd2ceaf on `filetypes/gz`

Cycle `20260526T222426-confirm-47ff785ebfd2ceaf` — 2026-05-26T22:24:26Z

PR_AUC held across 3 seeds (orig 0.9986)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `47ff785ebfd2ceaf` | `ff5f5e8bc271b368` | `ff5f5e8bc271b368` | `ff5f5e8bc271b368` |
| PR AUC | 0.9986 | 0.9984 | 0.9986 | 0.9985 |
| ROC AUC | 0.9982 | 0.9979 | 0.9981 | 0.9980 |
| Recall@3FPM | — | 0.9913 | 0.9913 | 0.9913 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=47ff785ebfd2ceaf
```
