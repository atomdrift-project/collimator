# Confirm PASS — b1651b24df6777b5 on `filegroups/media`

Cycle `20261112T202621-confirm-b1651b24df6777b5` — 2026-11-12T20:26:21Z

averaged 3-seed ensemble PR_AUC held: 0.9724 -> 0.9796; individual seeds may be noisy

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b1651b24df6777b5` | `a34d9a1fcf8b666a` | `a34d9a1fcf8b666a` | `a34d9a1fcf8b666a` |
| PR AUC | 0.9724 | 0.9787 | 0.9794 | 0.9784 |
| ROC AUC | 0.9955 | 0.9969 | 0.9970 | 0.9966 |
| Recall@L50 | — | 0.3035 | 0.3675 | 0.3227 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b1651b24df6777b5
```
