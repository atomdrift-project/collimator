# Confirm PASS — def0848db885ef54 on `filegroups/documents`

Cycle `20260606T112029-confirm-def0848db885ef54` — 2026-06-06T11:20:29Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `def0848db885ef54` | `48e711ddf647f0d6` | `48e711ddf647f0d6` | `48e711ddf647f0d6` |
| PR AUC | 1.0000 | 0.9999 | 1.0000 | 1.0000 |
| ROC AUC | 0.9995 | 0.9971 | 0.9993 | 0.9992 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=def0848db885ef54
```
