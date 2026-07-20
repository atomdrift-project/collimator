# Confirm PASS — 58fffcf3474fe8f8 on `filetypes/package.json`

Cycle `20260711T174900-confirm-58fffcf3474fe8f8` — 2026-07-11T17:49:00Z

PR_AUC held across 3 seeds (orig 0.9977)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `58fffcf3474fe8f8` | `be235feffce8a6a8` | `be235feffce8a6a8` | `be235feffce8a6a8` |
| PR AUC | 0.9977 | 0.9977 | 0.9979 | 0.9975 |
| ROC AUC | 0.9980 | 0.9979 | 0.9981 | 0.9979 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=58fffcf3474fe8f8
```
