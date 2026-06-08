# Confirm PASS — d77520ba8bd32f45 on `filetypes/jpeg`

Cycle `20260608T105933-confirm-d77520ba8bd32f45` — 2026-06-08T10:59:33Z

PR_AUC held across 3 seeds (orig 0.9478)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d77520ba8bd32f45` | `2c11550b609d17a6` | `2c11550b609d17a6` | `2c11550b609d17a6` |
| PR AUC | 0.9478 | 0.9581 | 0.9566 | 0.9642 |
| ROC AUC | 0.9733 | 0.9784 | 0.9755 | 0.9828 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d77520ba8bd32f45
```
