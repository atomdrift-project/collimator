# Confirm PASS — 831b4996d045dbdc on `filetypes/text`

Cycle `20261030T191654-confirm-831b4996d045dbdc` — 2026-10-30T19:16:54Z

averaged 3-seed ensemble PR_AUC held: 0.9180 -> 0.9381; individual seeds may be noisy

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `831b4996d045dbdc` | `3546e3721884c8ec` | `3546e3721884c8ec` | `3546e3721884c8ec` |
| PR AUC | 0.9180 | 0.9364 | 0.9337 | 0.9364 |
| ROC AUC | 0.9842 | 0.9847 | 0.9832 | 0.9838 |
| Recall@L50 | — | 0.2978 | 0.3935 | 0.3275 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=831b4996d045dbdc
```
