# Confirm PASS — 616baf33eb6111ea on `filegroups/portable`

Cycle `20260609T002244-confirm-616baf33eb6111ea` — 2026-06-09T00:22:44Z

PR_AUC held across 3 seeds (orig 0.9885)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `616baf33eb6111ea` | `e646a12ea3bb07dd` | `e646a12ea3bb07dd` | `e646a12ea3bb07dd` |
| PR AUC | 0.9885 | 0.9900 | 0.9890 | 0.9885 |
| ROC AUC | 0.9979 | 0.9982 | 0.9982 | 0.9979 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=616baf33eb6111ea
```
