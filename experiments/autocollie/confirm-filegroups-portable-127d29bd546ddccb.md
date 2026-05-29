# Confirm PASS — 127d29bd546ddccb on `filegroups/portable`

Cycle `20260527T012815-confirm-127d29bd546ddccb` — 2026-05-27T01:28:15Z

PR_AUC held across 3 seeds (orig 0.9967)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `127d29bd546ddccb` | `8cc9f5c56d99ef65` | `8cc9f5c56d99ef65` | `8cc9f5c56d99ef65` |
| PR AUC | 0.9967 | 0.9961 | 0.9948 | 0.9957 |
| ROC AUC | 0.9992 | 0.9990 | 0.9988 | 0.9989 |
| Recall@3FPM | — | 0.8200 | 0.7000 | 0.8667 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=127d29bd546ddccb
```
