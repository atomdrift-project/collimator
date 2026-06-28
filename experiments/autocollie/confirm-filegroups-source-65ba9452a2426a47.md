# Confirm PASS — 65ba9452a2426a47 on `filegroups/source`

Cycle `20260628T135904-confirm-65ba9452a2426a47` — 2026-06-28T13:59:04Z

PR_AUC held across 3 seeds (orig 0.9956)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `65ba9452a2426a47` | `bc9d4bb5a9c49cb1` | `bc9d4bb5a9c49cb1` | `bc9d4bb5a9c49cb1` |
| PR AUC | 0.9956 | 0.9966 | 0.9964 | 0.9966 |
| ROC AUC | 0.9960 | 0.9969 | 0.9968 | 0.9969 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=65ba9452a2426a47
```
