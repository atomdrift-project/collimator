# Confirm PASS — d037376487c6b9ae on `filetypes/xls`

Cycle `20260526T174852-confirm-d037376487c6b9ae` — 2026-05-26T17:48:52Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d037376487c6b9ae` | `0870c77ce3361485` | `0870c77ce3361485` | `0870c77ce3361485` |
| PR AUC | 0.9999 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9996 | 0.9996 | 0.9996 | 0.9996 |
| Recall@3FPM | — | 0.9864 | 0.9887 | 0.9879 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d037376487c6b9ae
```
