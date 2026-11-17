# Confirm PASS — 1ae127d276cede81 on `filegroups/source`

Cycle `20261112T203149-confirm-1ae127d276cede81` — 2026-11-12T20:31:49Z

averaged 3-seed ensemble PR_AUC held: 0.9828 -> 0.9895; individual seeds may be noisy

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `1ae127d276cede81` | `e61a09d820415883` | `e61a09d820415883` | `e61a09d820415883` |
| PR AUC | 0.9828 | 0.9883 | 0.9898 | 0.9888 |
| ROC AUC | 0.9810 | 0.9875 | 0.9893 | 0.9883 |
| Recall@L50 | — | 0.6607 | 0.6825 | 0.6008 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=1ae127d276cede81
```
