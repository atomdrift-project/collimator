# Confirm PASS — 09e3314e33835065 on `filegroups/documents`

Cycle `20260523T200532-confirm-09e3314e33835065` — 2026-05-23T20:05:32Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `09e3314e33835065` | `3685bacbeac831ad` | `3685bacbeac831ad` | `3685bacbeac831ad` |
| PR AUC | 1.0000 | 0.9996 | 0.9996 | 0.9995 |
| ROC AUC | 0.9985 | 0.9668 | 0.9679 | 0.9599 |
| Recall@3FPM | — | 0.7039 | 0.7039 | 0.6532 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=09e3314e33835065
```
