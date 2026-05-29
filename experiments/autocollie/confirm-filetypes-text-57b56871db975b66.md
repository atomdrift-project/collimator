# Confirm PASS — 57b56871db975b66 on `filetypes/text`

Cycle `20260527T015241-confirm-57b56871db975b66` — 2026-05-27T01:52:41Z

PR_AUC held across 3 seeds (orig 0.9691)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `57b56871db975b66` | `d7f5b5f653854a33` | `d7f5b5f653854a33` | `d7f5b5f653854a33` |
| PR AUC | 0.9691 | 0.9581 | 0.9740 | 0.9672 |
| ROC AUC | 0.9851 | 0.9826 | 0.9881 | 0.9826 |
| Recall@3FPM | — | 0.6190 | 0.8095 | 0.8571 |
| verdict | — | FAIL | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=57b56871db975b66
```
