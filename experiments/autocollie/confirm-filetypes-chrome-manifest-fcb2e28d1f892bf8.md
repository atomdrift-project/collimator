# Confirm PASS — fcb2e28d1f892bf8 on `filetypes/chrome-manifest`

Cycle `20260527T015619-confirm-fcb2e28d1f892bf8` — 2026-05-27T01:56:19Z

PR_AUC held across 3 seeds (orig 0.8588)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `fcb2e28d1f892bf8` | `4f3ba94b130b75db` | `4f3ba94b130b75db` | `4f3ba94b130b75db` |
| PR AUC | 0.8588 | 0.5388 | 0.8714 | 0.8600 |
| ROC AUC | 0.9385 | 0.8872 | 0.9538 | 0.9692 |
| Recall@3FPM | — | 0.0000 | 0.8000 | 0.6000 |
| verdict | — | FAIL | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=fcb2e28d1f892bf8
```
