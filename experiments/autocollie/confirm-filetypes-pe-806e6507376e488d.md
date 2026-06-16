# Confirm PASS — 806e6507376e488d on `filetypes/pe`

Cycle `20260616T073742-confirm-806e6507376e488d` — 2026-06-16T07:37:42Z

PR_AUC held across 3 seeds (orig 0.9989)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `806e6507376e488d` | `4cd91e37bfcd090e` | `4cd91e37bfcd090e` | `4cd91e37bfcd090e` |
| PR AUC | 0.9989 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9990 | 0.9998 | 0.9998 | 0.9998 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=806e6507376e488d
```
