# Confirm PASS — 6d57c5e8ea707aad on `filegroups/source`

Cycle `20260526T030609-confirm-6d57c5e8ea707aad` — 2026-05-26T03:06:09Z

PR_AUC held across 3 seeds (orig 0.9983)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6d57c5e8ea707aad` | `c86e76f095d74d24` | `c86e76f095d74d24` | `c86e76f095d74d24` |
| PR AUC | 0.9983 | 0.9988 | 0.9988 | 0.9988 |
| ROC AUC | 0.9973 | 0.9977 | 0.9978 | 0.9977 |
| Recall@3FPM | — | 0.8858 | 0.9065 | 0.9065 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=6d57c5e8ea707aad
```
