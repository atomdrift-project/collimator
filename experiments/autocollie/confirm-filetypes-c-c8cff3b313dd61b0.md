# Confirm PASS — c8cff3b313dd61b0 on `filetypes/c`

Cycle `20261112T123012-confirm-c8cff3b313dd61b0` — 2026-11-12T12:30:12Z

averaged 3-seed ensemble PR_AUC held: 0.9934 -> 0.9963; individual seeds may be noisy

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c8cff3b313dd61b0` | `6c863253b7999ef1` | `6c863253b7999ef1` | `6c863253b7999ef1` |
| PR AUC | 0.9934 | 0.9942 | 0.9951 | 0.9952 |
| ROC AUC | 0.9977 | 0.9978 | 0.9982 | 0.9982 |
| Recall@L50 | — | 0.8409 | 0.8199 | 0.8701 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=c8cff3b313dd61b0
```
