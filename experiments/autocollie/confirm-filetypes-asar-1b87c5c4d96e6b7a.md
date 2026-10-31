# Confirm PASS — 1b87c5c4d96e6b7a on `filetypes/asar`

Cycle `20261030T214841-confirm-1b87c5c4d96e6b7a` — 2026-10-30T21:48:41Z

averaged 3-seed ensemble PR_AUC held: 0.9992 -> 1.0000; individual seeds may be noisy

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `1b87c5c4d96e6b7a` | `1d1a0ea64d82ff7c` | `1d1a0ea64d82ff7c` | `1d1a0ea64d82ff7c` |
| PR AUC | 0.9992 | 0.9992 | 1.0000 | 1.0000 |
| ROC AUC | 0.9994 | 0.9994 | 1.0000 | 1.0000 |
| Recall@L50 | — | 0.9714 | 1.0000 | 1.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=1b87c5c4d96e6b7a
```
