# Confirm PASS — e70afc503f0c4336 on `filegroups/documents`

Cycle `20260526T221227-confirm-e70afc503f0c4336` — 2026-05-26T22:12:27Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e70afc503f0c4336` | `911b8de6198fd928` | `911b8de6198fd928` | `911b8de6198fd928` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9991 | 0.9997 | 0.9997 | 0.9997 |
| Recall@3FPM | — | 0.9793 | 0.9570 | 0.9703 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e70afc503f0c4336
```
