# Confirm PASS — ec8d6fc93e024550 on `filetypes/batch`

Cycle `20260603T161545-confirm-ec8d6fc93e024550` — 2026-06-03T16:15:45Z

PR_AUC held across 3 seeds (orig 0.9998)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ec8d6fc93e024550` | `a41fc92b01a0341c` | `a41fc92b01a0341c` | `a41fc92b01a0341c` |
| PR AUC | 0.9998 | 0.9998 | 0.9998 | 0.9997 |
| ROC AUC | 0.9978 | 0.9979 | 0.9977 | 0.9966 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=ec8d6fc93e024550
```
