# Confirm PASS — eb81d8e3120f3aed on `filegroups/source`

Cycle `20260711T144152-confirm-eb81d8e3120f3aed` — 2026-07-11T14:41:52Z

PR_AUC held across 3 seeds (orig 0.9932)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `eb81d8e3120f3aed` | `5afe1610f4deb4c2` | `5afe1610f4deb4c2` | `5afe1610f4deb4c2` |
| PR AUC | 0.9932 | 0.9949 | 0.9949 | 0.9948 |
| ROC AUC | 0.9953 | 0.9965 | 0.9965 | 0.9962 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=eb81d8e3120f3aed
```
