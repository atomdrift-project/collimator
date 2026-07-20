# Confirm PASS — 436a51a79d5c7880 on `filetypes/ole`

Cycle `20260715T083846-confirm-436a51a79d5c7880` — 2026-07-15T08:38:46Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `436a51a79d5c7880` | `dc568ae6e8a29552` | `dc568ae6e8a29552` | `dc568ae6e8a29552` |
| PR AUC | 0.9999 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9991 | 0.9990 | 0.9991 | 0.9991 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=436a51a79d5c7880
```
