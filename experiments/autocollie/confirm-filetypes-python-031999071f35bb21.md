# Confirm PASS — 031999071f35bb21 on `filetypes/python`

Cycle `20260601T213614-confirm-031999071f35bb21` — 2026-06-01T21:36:14Z

PR_AUC held across 3 seeds (orig 0.9990)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `031999071f35bb21` | `598b2d294025434b` | `598b2d294025434b` | `598b2d294025434b` |
| PR AUC | 0.9990 | 0.9972 | 0.9975 | 0.9973 |
| ROC AUC | 0.9991 | 0.9979 | 0.9982 | 0.9980 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=031999071f35bb21
```
