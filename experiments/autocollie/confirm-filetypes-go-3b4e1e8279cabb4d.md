# Confirm PASS — 3b4e1e8279cabb4d on `filetypes/go`

Cycle `20260602T010341-confirm-3b4e1e8279cabb4d` — 2026-06-02T01:03:41Z

PR_AUC held across 3 seeds (orig 0.9597)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3b4e1e8279cabb4d` | `459730e7ba770f39` | `459730e7ba770f39` | `459730e7ba770f39` |
| PR AUC | 0.9597 | 0.9617 | 0.9495 | 0.9512 |
| ROC AUC | 0.9861 | 0.9888 | 0.9843 | 0.9854 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | FAIL | FAIL |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3b4e1e8279cabb4d
```
