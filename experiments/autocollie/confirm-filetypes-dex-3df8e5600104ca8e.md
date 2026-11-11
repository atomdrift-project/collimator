# Confirm PASS — 3df8e5600104ca8e on `filetypes/dex`

Cycle `20261110T195818-confirm-3df8e5600104ca8e` — 2026-11-10T19:58:18Z

averaged 3-seed ensemble PR_AUC held: 1.0000 -> 1.0000; individual seeds may be noisy

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3df8e5600104ca8e` | `ab00108fe7bbd634` | `ab00108fe7bbd634` | `ab00108fe7bbd634` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@L50 | — | 1.0000 | 1.0000 | 1.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3df8e5600104ca8e
```
