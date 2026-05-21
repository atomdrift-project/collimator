# Confirm PASS — 21e1d79b81ba49dd on `filegroups/source`

Cycle `20260521T070039-confirm-21e1d79b81ba49dd` — 2026-05-21T07:00:39Z

PR_AUC held across 3 seeds (orig 0.9988)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `21e1d79b81ba49dd` | `a394fb28b17230e4` | `a394fb28b17230e4` | `a394fb28b17230e4` |
| PR AUC | 0.9988 | 0.9988 | 0.9988 | 0.9988 |
| ROC AUC | 0.9982 | 0.9981 | 0.9981 | 0.9981 |
| Recall@3FPM | — | 0.8897 | 0.8990 | 0.9194 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=21e1d79b81ba49dd
```
