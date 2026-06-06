# Confirm PASS — 7d0007f049c9b2d1 on `filetypes/python`

Cycle `20260606T201716-confirm-7d0007f049c9b2d1` — 2026-06-06T20:17:16Z

PR_AUC held across 3 seeds (orig 0.9953)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `7d0007f049c9b2d1` | `a7b67b3e2aea9331` | `a7b67b3e2aea9331` | `a7b67b3e2aea9331` |
| PR AUC | 0.9953 | 0.9957 | 0.9954 | 0.9955 |
| ROC AUC | 0.9962 | 0.9965 | 0.9962 | 0.9964 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=7d0007f049c9b2d1
```
