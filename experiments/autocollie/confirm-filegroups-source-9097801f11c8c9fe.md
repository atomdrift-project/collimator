# Confirm PASS — 9097801f11c8c9fe on `filegroups/source`

Cycle `20261030T213505-confirm-9097801f11c8c9fe` — 2026-10-30T21:35:05Z

averaged 3-seed ensemble PR_AUC held: 0.9865 -> 0.9869; individual seeds may be noisy

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `9097801f11c8c9fe` | `d1bf268e35cd2960` | `d1bf268e35cd2960` | `d1bf268e35cd2960` |
| PR AUC | 0.9865 | 0.9858 | 0.9857 | 0.9856 |
| ROC AUC | 0.9858 | 0.9839 | 0.9848 | 0.9843 |
| Recall@L50 | — | 0.4558 | 0.4437 | 0.4339 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=9097801f11c8c9fe
```
