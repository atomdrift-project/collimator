# Confirm PASS — fa5823cbed9d49a4 on `filegroups/documents`

Cycle `20260525T202450-confirm-fa5823cbed9d49a4` — 2026-05-25T20:24:50Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `fa5823cbed9d49a4` | `3213e1fdd0123bde` | `3213e1fdd0123bde` | `3213e1fdd0123bde` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9991 | 0.9996 | 0.9997 | 0.9997 |
| Recall@3FPM | — | 0.9720 | 0.9732 | 0.9801 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=fa5823cbed9d49a4
```
