# Confirm PASS — 628c54d7d3611a69 on `filegroups/media`

Cycle `20260609T110935-confirm-628c54d7d3611a69` — 2026-06-09T11:09:35Z

PR_AUC held across 3 seeds (orig 0.9717)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `628c54d7d3611a69` | `dfcdfcadfb0889e2` | `dfcdfcadfb0889e2` | `dfcdfcadfb0889e2` |
| PR AUC | 0.9717 | 0.9793 | 0.9708 | 0.9746 |
| ROC AUC | 0.9798 | 0.9876 | 0.9828 | 0.9823 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=628c54d7d3611a69
```
