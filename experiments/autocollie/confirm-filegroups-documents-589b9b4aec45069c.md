# Confirm PASS — 589b9b4aec45069c on `filegroups/documents`

Cycle `20260526T220841-confirm-589b9b4aec45069c` — 2026-05-26T22:08:41Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `589b9b4aec45069c` | `6049956f792caeca` | `6049956f792caeca` | `6049956f792caeca` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9991 | 0.9997 | 0.9997 | 0.9997 |
| Recall@3FPM | — | 0.9795 | 0.9732 | 0.9811 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=589b9b4aec45069c
```
