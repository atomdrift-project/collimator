# Confirm PASS — 945d65a3820c99d6 on `filegroups/native`

Cycle `20260627T143745-confirm-945d65a3820c99d6` — 2026-06-27T14:37:45Z

PR_AUC held across 3 seeds (orig 0.9994)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `945d65a3820c99d6` | `bad3e0c7594a11f6` | `bad3e0c7594a11f6` | `bad3e0c7594a11f6` |
| PR AUC | 0.9994 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9994 | 0.9999 | 0.9998 | 0.9998 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=945d65a3820c99d6
```
