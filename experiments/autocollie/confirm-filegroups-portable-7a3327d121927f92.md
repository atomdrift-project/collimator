# Confirm PASS — 7a3327d121927f92 on `filegroups/portable`

Cycle `20260615T053706-confirm-7a3327d121927f92` — 2026-06-15T05:37:06Z

PR_AUC held across 3 seeds (orig 0.9874)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `7a3327d121927f92` | `f0178d671fd5da7b` | `f0178d671fd5da7b` | `f0178d671fd5da7b` |
| PR AUC | 0.9874 | 0.9871 | 0.9870 | 0.9889 |
| ROC AUC | 0.9977 | 0.9976 | 0.9974 | 0.9979 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=7a3327d121927f92
```
