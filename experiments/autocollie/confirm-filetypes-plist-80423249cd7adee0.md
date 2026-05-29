# Confirm PASS — 80423249cd7adee0 on `filetypes/plist`

Cycle `20260527T062151-confirm-80423249cd7adee0` — 2026-05-27T06:21:51Z

PR_AUC held across 3 seeds (orig 0.2000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `80423249cd7adee0` | `6f1584e87399c01e` | `6f1584e87399c01e` | `6f1584e87399c01e` |
| PR AUC | 0.2000 | 0.2000 | 0.2000 | 0.2000 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=80423249cd7adee0
```
