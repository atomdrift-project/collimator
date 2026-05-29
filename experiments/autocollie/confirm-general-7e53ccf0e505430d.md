# Confirm PASS — 7e53ccf0e505430d on `general`

Cycle `20260527T050155-confirm-7e53ccf0e505430d` — 2026-05-27T05:01:55Z

PR_AUC held across 3 seeds (orig 0.9997)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `7e53ccf0e505430d` | `6aebb3b19bf8cf3d` | `6aebb3b19bf8cf3d` | `6aebb3b19bf8cf3d` |
| PR AUC | 0.9997 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9997 | 0.9997 | 0.9997 | 0.9997 |
| Recall@3FPM | — | 0.5650 | 0.6430 | 0.5255 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=7e53ccf0e505430d
```
