# Confirm PASS — 12af87a2d2f5021a on `filetypes/jar`

Cycle `20260526T233031-confirm-12af87a2d2f5021a` — 2026-05-26T23:30:31Z

PR_AUC held across 3 seeds (orig 0.9988)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `12af87a2d2f5021a` | `eaf367d6ccb141c3` | `eaf367d6ccb141c3` | `eaf367d6ccb141c3` |
| PR AUC | 0.9988 | 0.9973 | 0.9984 | 0.9984 |
| ROC AUC | 0.9977 | 0.9941 | 0.9971 | 0.9970 |
| Recall@3FPM | — | 0.8807 | 0.8636 | 0.9091 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=12af87a2d2f5021a
```
