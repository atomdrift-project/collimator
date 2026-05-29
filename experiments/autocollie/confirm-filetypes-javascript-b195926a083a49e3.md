# Confirm PASS — b195926a083a49e3 on `filetypes/javascript`

Cycle `20260526T061539-confirm-b195926a083a49e3` — 2026-05-26T06:15:39Z

PR_AUC held across 3 seeds (orig 0.9993)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b195926a083a49e3` | `a2c3d5a3977d36c7` | `a2c3d5a3977d36c7` | `a2c3d5a3977d36c7` |
| PR AUC | 0.9993 | 0.9997 | 0.9997 | 0.9997 |
| ROC AUC | 0.9989 | 0.9995 | 0.9995 | 0.9995 |
| Recall@3FPM | — | 0.8439 | 0.8715 | 0.8914 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b195926a083a49e3
```
