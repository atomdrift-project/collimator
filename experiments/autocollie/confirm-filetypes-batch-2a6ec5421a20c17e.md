# Confirm PASS — 2a6ec5421a20c17e on `filetypes/batch`

Cycle `20260825T000037-confirm-2a6ec5421a20c17e` — 2026-08-25T00:00:37Z

PR_AUC held across 3 seeds (orig 0.9990)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `2a6ec5421a20c17e` | `e23ce042d20a421a` | `e23ce042d20a421a` | `e23ce042d20a421a` |
| PR AUC | 0.9990 | 0.9986 | 0.9993 | 0.9997 |
| ROC AUC | 0.9929 | 0.9776 | 0.9893 | 0.9957 |
| Recall@L50 | — | 0.1715 | 0.1729 | 0.1882 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=2a6ec5421a20c17e
```
