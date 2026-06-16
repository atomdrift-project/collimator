# Confirm PASS — 4919704f9d88a5a8 on `filetypes/shell`

Cycle `20260616T101543-confirm-4919704f9d88a5a8` — 2026-06-16T10:15:43Z

PR_AUC held across 3 seeds (orig 0.9977)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `4919704f9d88a5a8` | `bb2b089638d31785` | `bb2b089638d31785` | `bb2b089638d31785` |
| PR AUC | 0.9977 | 0.9976 | 0.9975 | 0.9975 |
| ROC AUC | 0.9977 | 0.9977 | 0.9975 | 0.9975 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=4919704f9d88a5a8
```
