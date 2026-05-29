# Confirm PASS — e0c417e613b90368 on `filegroups/config`

Cycle `20260526T145001-confirm-e0c417e613b90368` — 2026-05-26T14:50:01Z

PR_AUC held across 3 seeds (orig 0.9997)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e0c417e613b90368` | `700a68df052b296d` | `700a68df052b296d` | `700a68df052b296d` |
| PR AUC | 0.9997 | 0.9998 | 0.9998 | 0.9999 |
| ROC AUC | 0.9995 | 0.9997 | 0.9997 | 0.9998 |
| Recall@3FPM | — | 0.8587 | 0.8157 | 0.9509 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e0c417e613b90368
```
