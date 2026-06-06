# Confirm PASS — cf42b87e2b09ea4e on `filetypes/ole`

Cycle `20260606T112329-confirm-cf42b87e2b09ea4e` — 2026-06-06T11:23:29Z

PR_AUC held across 3 seeds (orig 0.9979)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `cf42b87e2b09ea4e` | `3ab422b8ea090b04` | `3ab422b8ea090b04` | `3ab422b8ea090b04` |
| PR AUC | 0.9979 | 0.9978 | 0.9971 | 0.9978 |
| ROC AUC | 0.9975 | 0.9973 | 0.9966 | 0.9972 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=cf42b87e2b09ea4e
```
