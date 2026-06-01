# Confirm PASS — cef5d8b792ac1291 on `filetypes/javascript`

Cycle `20260601T175213-confirm-cef5d8b792ac1291` — 2026-06-01T17:52:13Z

PR_AUC held across 3 seeds (orig 0.9993)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `cef5d8b792ac1291` | `637bef2d90065950` | `637bef2d90065950` | `637bef2d90065950` |
| PR AUC | 0.9993 | 0.9993 | 0.9993 | 0.9993 |
| ROC AUC | 0.9989 | 0.9990 | 0.9990 | 0.9990 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=cef5d8b792ac1291
```
