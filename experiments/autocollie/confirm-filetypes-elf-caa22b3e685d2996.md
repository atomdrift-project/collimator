# Confirm PASS — caa22b3e685d2996 on `filetypes/elf`

Cycle `20260526T155525-confirm-caa22b3e685d2996` — 2026-05-26T15:55:25Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `caa22b3e685d2996` | `847462513bf121a8` | `847462513bf121a8` | `847462513bf121a8` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 0.9813 | 0.9791 | 0.9756 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=caa22b3e685d2996
```
