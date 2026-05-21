# Confirm PASS — 5844919dc0d3e27a on `filegroups/documents`

Cycle `20260521T083444-confirm-5844919dc0d3e27a` — 2026-05-21T08:34:44Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `5844919dc0d3e27a` | `9971aebc51c9247b` | `9971aebc51c9247b` | `9971aebc51c9247b` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9991 | 0.9986 | 0.9986 | 0.9986 |
| Recall@3FPM | — | 0.9868 | 0.9866 | 0.9867 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=5844919dc0d3e27a
```
