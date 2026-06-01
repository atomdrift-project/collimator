# Confirm PASS — 3c05a7ec6a568d12 on `filegroups/source`

Cycle `20260601T135134-confirm-3c05a7ec6a568d12` — 2026-06-01T13:51:34Z

PR_AUC held across 3 seeds (orig 0.9991)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3c05a7ec6a568d12` | `69d94d637127b0f5` | `69d94d637127b0f5` | `69d94d637127b0f5` |
| PR AUC | 0.9991 | 0.9988 | 0.9989 | 0.9988 |
| ROC AUC | 0.9984 | 0.9981 | 0.9982 | 0.9980 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3c05a7ec6a568d12
```
