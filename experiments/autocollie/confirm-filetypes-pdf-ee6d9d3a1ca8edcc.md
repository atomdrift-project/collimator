# Confirm PASS — ee6d9d3a1ca8edcc on `filetypes/pdf`

Cycle `20260514T190635-confirm-ee6d9d3a1ca8edcc` — 2026-05-14T19:06:35Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ee6d9d3a1ca8edcc` | `56c23e6c2233c3ed` | `56c23e6c2233c3ed` | `56c23e6c2233c3ed` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9988 | 0.9989 | 0.9988 | 0.9976 |
| Recall@3FPM | — | 0.9916 | 0.9904 | 0.9848 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=ee6d9d3a1ca8edcc
```
