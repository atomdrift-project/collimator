# Confirm PASS — 12af87a2d2f5021a on `filetypes/jar`

Cycle `20260521T093729-confirm-12af87a2d2f5021a` — 2026-05-21T09:37:29Z

PR_AUC held across 3 seeds (orig 0.9988)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `12af87a2d2f5021a` | `b3782da69bb630e0` | `b3782da69bb630e0` | `b3782da69bb630e0` |
| PR AUC | 0.9988 | 0.9976 | 0.9988 | 0.9976 |
| ROC AUC | 0.9977 | 0.9956 | 0.9977 | 0.9954 |
| Recall@3FPM | — | 0.7882 | 0.9294 | 0.9059 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=12af87a2d2f5021a
```
