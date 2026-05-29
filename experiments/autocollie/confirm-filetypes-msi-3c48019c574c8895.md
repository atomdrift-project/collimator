# Confirm PASS — 3c48019c574c8895 on `filetypes/msi`

Cycle `20260526T215012-confirm-3c48019c574c8895` — 2026-05-26T21:50:12Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3c48019c574c8895` | `0f5ac6d9fe86b9f1` | `0f5ac6d9fe86b9f1` | `0f5ac6d9fe86b9f1` |
| PR AUC | 1.0000 | 0.9996 | 0.9996 | 0.9993 |
| ROC AUC | 1.0000 | 0.9888 | 0.9883 | 0.9803 |
| Recall@3FPM | — | 0.9667 | 0.9667 | 0.9600 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3c48019c574c8895
```
