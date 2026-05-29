# Confirm PASS — 5f90b5f6ac27d052 on `filetypes/github-actions`

Cycle `20260527T060405-confirm-5f90b5f6ac27d052` — 2026-05-27T06:04:05Z

PR_AUC held across 3 seeds (orig 0.0089)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `5f90b5f6ac27d052` | `c4696b8a052518a0` | `c4696b8a052518a0` | `c4696b8a052518a0` |
| PR AUC | 0.0089 | 0.0273 | 0.0273 | 0.0273 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=5f90b5f6ac27d052
```
