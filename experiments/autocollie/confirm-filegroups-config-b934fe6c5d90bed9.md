# Confirm PASS — b934fe6c5d90bed9 on `filegroups/config`

Cycle `20261030T210149-confirm-b934fe6c5d90bed9` — 2026-10-30T21:01:49Z

averaged 3-seed ensemble PR_AUC held: 0.9757 -> 0.9789; individual seeds may be noisy

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b934fe6c5d90bed9` | `a3beb52955e78629` | `a3beb52955e78629` | `a3beb52955e78629` |
| PR AUC | 0.9757 | 0.9782 | 0.9784 | 0.9790 |
| ROC AUC | 0.9812 | 0.9823 | 0.9823 | 0.9832 |
| Recall@L50 | — | 0.8243 | 0.8560 | 0.8598 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b934fe6c5d90bed9
```
