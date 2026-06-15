# Confirm PASS — cd476b9f7e787b85 on `filetypes/jpeg`

Cycle `20260615T060619-confirm-cd476b9f7e787b85` — 2026-06-15T06:06:19Z

PR_AUC held across 3 seeds (orig 0.9513)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `cd476b9f7e787b85` | `9988ce2d71fe1b8a` | `9988ce2d71fe1b8a` | `9988ce2d71fe1b8a` |
| PR AUC | 0.9513 | 0.9743 | 0.9548 | 0.9557 |
| ROC AUC | 0.9755 | 0.9861 | 0.9775 | 0.9765 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=cd476b9f7e787b85
```
