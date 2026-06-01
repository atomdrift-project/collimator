# Confirm PASS — 28d80e75a348c1ee on `filegroups/source`

Cycle `20260601T144657-confirm-28d80e75a348c1ee` — 2026-06-01T14:46:57Z

PR_AUC held across 3 seeds (orig 0.9990)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `28d80e75a348c1ee` | `d866ad8607d65ca3` | `d866ad8607d65ca3` | `d866ad8607d65ca3` |
| PR AUC | 0.9990 | 0.9988 | 0.9988 | 0.9988 |
| ROC AUC | 0.9982 | 0.9980 | 0.9981 | 0.9981 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=28d80e75a348c1ee
```
