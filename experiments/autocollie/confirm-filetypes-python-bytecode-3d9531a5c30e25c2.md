# Confirm PASS — 3d9531a5c30e25c2 on `filetypes/python-bytecode`

Cycle `20260526T225245-confirm-3d9531a5c30e25c2` — 2026-05-26T22:52:45Z

PR_AUC held across 3 seeds (orig 0.9996)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3d9531a5c30e25c2` | `d1f17a9708d72c3d` | `d1f17a9708d72c3d` | `d1f17a9708d72c3d` |
| PR AUC | 0.9996 | 0.9987 | 0.9984 | 0.9989 |
| ROC AUC | 0.9974 | 0.9948 | 0.9935 | 0.9954 |
| Recall@3FPM | — | 0.9347 | 0.9102 | 0.9429 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3d9531a5c30e25c2
```
