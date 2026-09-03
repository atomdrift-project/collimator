# Confirm PASS — cbe9c6a264122fd6 on `filegroups/documents`

Cycle `20260825T011521-confirm-cbe9c6a264122fd6` — 2026-08-25T01:15:21Z

PR_AUC held across 3 seeds (orig 0.9825)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `cbe9c6a264122fd6` | `b8256851b9fcd660` | `b8256851b9fcd660` | `b8256851b9fcd660` |
| PR AUC | 0.9825 | 0.9959 | 0.9949 | 0.9965 |
| ROC AUC | 0.9795 | 0.9888 | 0.9861 | 0.9908 |
| Recall@L50 | — | 0.7102 | 0.7119 | 0.7179 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=cbe9c6a264122fd6
```
