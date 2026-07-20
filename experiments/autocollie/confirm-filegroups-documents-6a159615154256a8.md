# Confirm PASS — 6a159615154256a8 on `filegroups/documents`

Cycle `20260710T211350-confirm-6a159615154256a8` — 2026-07-10T21:13:50Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6a159615154256a8` | `b2cb3249b104b1c9` | `b2cb3249b104b1c9` | `b2cb3249b104b1c9` |
| PR AUC | 0.9999 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9989 | 0.9991 | 0.9992 | 0.9992 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=6a159615154256a8
```
