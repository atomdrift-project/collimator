# Confirm PASS — 1dc32c72b4620ae5 on `filegroups/config`

Cycle `20260526T154901-confirm-1dc32c72b4620ae5` — 2026-05-26T15:49:01Z

PR_AUC held across 3 seeds (orig 0.9998)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `1dc32c72b4620ae5` | `d49229f250c6cf9b` | `d49229f250c6cf9b` | `d49229f250c6cf9b` |
| PR AUC | 0.9998 | 0.9998 | 0.9998 | 0.9999 |
| ROC AUC | 0.9996 | 0.9997 | 0.9996 | 0.9997 |
| Recall@3FPM | — | 0.8674 | 0.8152 | 0.9500 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=1dc32c72b4620ae5
```
