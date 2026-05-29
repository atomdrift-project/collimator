# Confirm PASS — a00a88b19f61b1e2 on `filetypes/groovy`

Cycle `20260527T054317-confirm-a00a88b19f61b1e2` — 2026-05-27T05:43:17Z

PR_AUC held across 3 seeds (orig 0.0017)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a00a88b19f61b1e2` | `dbfae746ba06f124` | `dbfae746ba06f124` | `dbfae746ba06f124` |
| PR AUC | 0.0017 | 0.9403 | 0.9415 | 0.9379 |
| ROC AUC | 0.5000 | 0.9603 | 0.9751 | 0.9512 |
| Recall@3FPM | — | 0.8333 | 0.8333 | 0.8889 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a00a88b19f61b1e2
```
