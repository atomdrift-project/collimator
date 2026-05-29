# Confirm PASS — 7cdf4180be5877e3 on `filetypes/javascript`

Cycle `20260526T062655-confirm-7cdf4180be5877e3` — 2026-05-26T06:26:55Z

PR_AUC held across 3 seeds (orig 0.9993)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `7cdf4180be5877e3` | `ffbcbfd64688703a` | `ffbcbfd64688703a` | `ffbcbfd64688703a` |
| PR AUC | 0.9993 | 0.9996 | 0.9997 | 0.9996 |
| ROC AUC | 0.9989 | 0.9995 | 0.9995 | 0.9994 |
| Recall@3FPM | — | 0.8591 | 0.8861 | 0.8824 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=7cdf4180be5877e3
```
