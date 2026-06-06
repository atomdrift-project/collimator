# Confirm PASS — ad69ae9298b30a67 on `filetypes/powershell`

Cycle `20260606T134513-confirm-ad69ae9298b30a67` — 2026-06-06T13:45:13Z

PR_AUC held across 3 seeds (orig 0.9950)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ad69ae9298b30a67` | `b8de0b1869e6e597` | `b8de0b1869e6e597` | `b8de0b1869e6e597` |
| PR AUC | 0.9950 | 0.9952 | 0.9949 | 0.9937 |
| ROC AUC | 0.9880 | 0.9886 | 0.9879 | 0.9858 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=ad69ae9298b30a67
```
