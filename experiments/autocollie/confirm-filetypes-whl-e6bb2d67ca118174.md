# Confirm PASS — e6bb2d67ca118174 on `filetypes/whl`

Cycle `20260720T113410-confirm-e6bb2d67ca118174` — 2026-07-20T11:34:10Z

PR_AUC held across 3 seeds (orig 0.9666)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e6bb2d67ca118174` | `94749e446015336e` | `94749e446015336e` | `94749e446015336e` |
| PR AUC | 0.9666 | 0.9679 | 0.9669 | 0.9668 |
| ROC AUC | 0.9635 | 0.9669 | 0.9653 | 0.9691 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e6bb2d67ca118174
```
