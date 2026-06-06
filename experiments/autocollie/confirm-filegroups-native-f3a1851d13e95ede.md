# Confirm PASS — f3a1851d13e95ede on `filegroups/native`

Cycle `20260606T080050-confirm-f3a1851d13e95ede` — 2026-06-06T08:00:50Z

PR_AUC held across 3 seeds (orig 0.9994)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f3a1851d13e95ede` | `77b3ce874439a303` | `77b3ce874439a303` | `77b3ce874439a303` |
| PR AUC | 0.9994 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9994 | 0.9999 | 0.9999 | 0.9999 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f3a1851d13e95ede
```
