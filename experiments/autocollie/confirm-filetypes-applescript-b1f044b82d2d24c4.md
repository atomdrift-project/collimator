# Confirm PASS — b1f044b82d2d24c4 on `filetypes/applescript`

Cycle `20260527T065720-confirm-b1f044b82d2d24c4` — 2026-05-27T06:57:20Z

PR_AUC held across 3 seeds (orig 0.4000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b1f044b82d2d24c4` | `b341e065daa37e61` | `b341e065daa37e61` | `b341e065daa37e61` |
| PR AUC | 0.4000 | 0.4000 | 0.4000 | 0.4000 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b1f044b82d2d24c4
```
