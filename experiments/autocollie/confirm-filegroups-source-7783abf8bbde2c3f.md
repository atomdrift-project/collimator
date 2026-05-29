# Confirm PASS — 7783abf8bbde2c3f on `filegroups/source`

Cycle `20260526T031355-confirm-7783abf8bbde2c3f` — 2026-05-26T03:13:55Z

PR_AUC held across 3 seeds (orig 0.9988)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `7783abf8bbde2c3f` | `ba6b47cee96660ba` | `ba6b47cee96660ba` | `ba6b47cee96660ba` |
| PR AUC | 0.9988 | 0.9992 | 0.9991 | 0.9991 |
| ROC AUC | 0.9980 | 0.9985 | 0.9984 | 0.9984 |
| Recall@3FPM | — | 0.9201 | 0.9188 | 0.9113 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=7783abf8bbde2c3f
```
