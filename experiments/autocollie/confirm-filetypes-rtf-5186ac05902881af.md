# Confirm PASS — 5186ac05902881af on `filetypes/rtf`

Cycle `20260527T074251-confirm-5186ac05902881af` — 2026-05-27T07:42:51Z

PR_AUC held across 3 seeds (orig 0.9780)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `5186ac05902881af` | `56a54bd5eb6f5ae1` | `56a54bd5eb6f5ae1` | `56a54bd5eb6f5ae1` |
| PR AUC | 0.9780 | 0.9784 | 0.9784 | 0.9784 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=5186ac05902881af
```
