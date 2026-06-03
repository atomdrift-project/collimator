# Confirm PASS — d3450ac06c22edfa on `filegroups/portable`

Cycle `20260603T163424-confirm-d3450ac06c22edfa` — 2026-06-03T16:34:24Z

PR_AUC held across 3 seeds (orig 0.9976)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d3450ac06c22edfa` | `50ff4d78f81f5c78` | `50ff4d78f81f5c78` | `50ff4d78f81f5c78` |
| PR AUC | 0.9976 | 0.9964 | 0.9963 | 0.9944 |
| ROC AUC | 0.9996 | 0.9993 | 0.9994 | 0.9990 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d3450ac06c22edfa
```
