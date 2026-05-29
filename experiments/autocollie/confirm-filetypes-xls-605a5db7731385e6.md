# Confirm PASS — 605a5db7731385e6 on `filetypes/xls`

Cycle `20260526T184131-confirm-605a5db7731385e6` — 2026-05-26T18:41:31Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `605a5db7731385e6` | `be988dbfe3356149` | `be988dbfe3356149` | `be988dbfe3356149` |
| PR AUC | 0.9999 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9992 | 0.9992 | 0.9992 | 0.9992 |
| Recall@3FPM | — | 0.9751 | 0.9743 | 0.9751 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=605a5db7731385e6
```
