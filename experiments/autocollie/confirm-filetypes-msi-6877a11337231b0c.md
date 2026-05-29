# Confirm PASS — 6877a11337231b0c on `filetypes/msi`

Cycle `20260526T215104-confirm-6877a11337231b0c` — 2026-05-26T21:51:04Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6877a11337231b0c` | `5a5431a83331087a` | `5a5431a83331087a` | `5a5431a83331087a` |
| PR AUC | 1.0000 | 0.9999 | 0.9996 | 0.9999 |
| ROC AUC | 1.0000 | 0.9970 | 0.9895 | 0.9973 |
| Recall@3FPM | — | 0.9867 | 0.9667 | 0.9900 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=6877a11337231b0c
```
