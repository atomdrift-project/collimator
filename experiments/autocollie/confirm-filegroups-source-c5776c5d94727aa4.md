# Confirm PASS — c5776c5d94727aa4 on `filegroups/source`

Cycle `20260614T202845-confirm-c5776c5d94727aa4` — 2026-06-14T20:28:45Z

PR_AUC held across 3 seeds (orig 0.9990)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c5776c5d94727aa4` | `c5cc18c6d79be62d` | `c5cc18c6d79be62d` | `c5cc18c6d79be62d` |
| PR AUC | 0.9990 | 0.9973 | 0.9972 | 0.9973 |
| ROC AUC | 0.9981 | 0.9968 | 0.9968 | 0.9969 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=c5776c5d94727aa4
```
