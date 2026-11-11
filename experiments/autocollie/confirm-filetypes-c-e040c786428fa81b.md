# Confirm PASS — e040c786428fa81b on `filetypes/c`

Cycle `20261103T003018-confirm-e040c786428fa81b` — 2026-11-03T00:30:18Z

averaged 3-seed ensemble PR_AUC held: 0.9917 -> 0.9947; individual seeds may be noisy

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e040c786428fa81b` | `9ba75bc96c6e0b52` | `9ba75bc96c6e0b52` | `9ba75bc96c6e0b52` |
| PR AUC | 0.9917 | 0.9931 | 0.9935 | 0.9930 |
| ROC AUC | 0.9972 | 0.9970 | 0.9973 | 0.9969 |
| Recall@L50 | — | 0.8005 | 0.8355 | 0.8013 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e040c786428fa81b
```
