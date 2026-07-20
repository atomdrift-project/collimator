# Confirm PASS — 4daaba2f77b4b511 on `filegroups/source`

Cycle `20260715T103430-confirm-4daaba2f77b4b511` — 2026-07-15T10:34:30Z

PR_AUC held across 3 seeds (orig 0.9935)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `4daaba2f77b4b511` | `71d03dbcb66eb9cf` | `71d03dbcb66eb9cf` | `71d03dbcb66eb9cf` |
| PR AUC | 0.9935 | 0.9948 | 0.9949 | 0.9945 |
| ROC AUC | 0.9956 | 0.9964 | 0.9965 | 0.9961 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=4daaba2f77b4b511
```
