# Confirm PASS — 5844919dc0d3e27a on `filegroups/documents`

Cycle `20260526T220113-confirm-5844919dc0d3e27a` — 2026-05-26T22:01:13Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `5844919dc0d3e27a` | `3813df9e49e5b779` | `3813df9e49e5b779` | `3813df9e49e5b779` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9991 | 0.9997 | 0.9997 | 0.9997 |
| Recall@3FPM | — | 0.9779 | 0.9732 | 0.9804 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=5844919dc0d3e27a
```
