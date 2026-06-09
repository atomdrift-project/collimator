# Confirm PASS — 988fb2100164d109 on `filegroups/source`

Cycle `20260609T105408-confirm-988fb2100164d109` — 2026-06-09T10:54:08Z

PR_AUC held across 3 seeds (orig 0.9978)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `988fb2100164d109` | `d827967841fa0d03` | `d827967841fa0d03` | `d827967841fa0d03` |
| PR AUC | 0.9978 | 0.9982 | 0.9982 | 0.9982 |
| ROC AUC | 0.9972 | 0.9976 | 0.9977 | 0.9976 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=988fb2100164d109
```
