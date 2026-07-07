# Confirm PASS — 1fd15fc86cbf4969 on `filetypes/vbs`

Cycle `20260706T044350-confirm-1fd15fc86cbf4969` — 2026-07-06T04:43:50Z

PR_AUC held across 3 seeds (orig 0.9998)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `1fd15fc86cbf4969` | `dec4db1237721837` | `dec4db1237721837` | `dec4db1237721837` |
| PR AUC | 0.9998 | 0.9999 | 0.9998 | 0.9978 |
| ROC AUC | 0.9973 | 0.9975 | 0.9971 | 0.9674 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=1fd15fc86cbf4969
```
