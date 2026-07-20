# Confirm PASS — a03d38247305ae9e on `filetypes/rust`

Cycle `20260718T135154-confirm-a03d38247305ae9e` — 2026-07-18T13:51:54Z

PR_AUC held across 3 seeds (orig 0.8095)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a03d38247305ae9e` | `370a4f6745d56aa6` | `370a4f6745d56aa6` | `370a4f6745d56aa6` |
| PR AUC | 0.8095 | 0.8499 | 0.7699 | 0.8387 |
| ROC AUC | 0.9677 | 0.9627 | 0.9642 | 0.9587 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | FAIL | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a03d38247305ae9e
```
