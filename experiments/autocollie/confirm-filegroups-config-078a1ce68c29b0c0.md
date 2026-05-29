# Confirm PASS — 078a1ce68c29b0c0 on `filegroups/config`

Cycle `20260526T150604-confirm-078a1ce68c29b0c0` — 2026-05-26T15:06:04Z

PR_AUC held across 3 seeds (orig 0.9997)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `078a1ce68c29b0c0` | `b8436e57ad0fd1a3` | `b8436e57ad0fd1a3` | `b8436e57ad0fd1a3` |
| PR AUC | 0.9997 | 0.9998 | 0.9998 | 0.9998 |
| ROC AUC | 0.9995 | 0.9997 | 0.9997 | 0.9997 |
| Recall@3FPM | — | 0.8739 | 0.8591 | 0.9461 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=078a1ce68c29b0c0
```
