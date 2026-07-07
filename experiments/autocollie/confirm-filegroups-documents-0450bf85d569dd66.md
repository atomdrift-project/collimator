# Confirm PASS — 0450bf85d569dd66 on `filegroups/documents`

Cycle `20260706T051606-confirm-0450bf85d569dd66` — 2026-07-06T05:16:06Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0450bf85d569dd66` | `c4a5b2c3bd4bf63b` | `c4a5b2c3bd4bf63b` | `c4a5b2c3bd4bf63b` |
| PR AUC | 0.9999 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9988 | 0.9992 | 0.9991 | 0.9992 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0450bf85d569dd66
```
