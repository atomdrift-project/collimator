# Confirm PASS — d194e30c2145fac5 on `filegroups/documents`

Cycle `20260826T231621-confirm-d194e30c2145fac5` — 2026-08-26T23:16:21Z

PR_AUC held across 3 seeds (orig 0.9811)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d194e30c2145fac5` | `1bc137e20eaad336` | `1bc137e20eaad336` | `1bc137e20eaad336` |
| PR AUC | 0.9811 | 0.9954 | 0.9952 | 0.9952 |
| ROC AUC | 0.9767 | 0.9876 | 0.9871 | 0.9871 |
| Recall@L50 | — | 0.7124 | 0.7043 | 0.7096 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d194e30c2145fac5
```
