# Confirm PASS — 12c04f8843366ad0 on `filetypes/javascript`

Cycle `20260524T151456-confirm-12c04f8843366ad0` — 2026-05-24T15:14:56Z

PR_AUC held across 3 seeds (orig 0.9993)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `12c04f8843366ad0` | `007dc84fd3473d5c` | `007dc84fd3473d5c` | `007dc84fd3473d5c` |
| PR AUC | 0.9993 | 0.9996 | 0.9997 | 0.9996 |
| ROC AUC | 0.9989 | 0.9995 | 0.9995 | 0.9994 |
| Recall@3FPM | — | 0.8690 | 0.8809 | 0.8737 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=12c04f8843366ad0
```
