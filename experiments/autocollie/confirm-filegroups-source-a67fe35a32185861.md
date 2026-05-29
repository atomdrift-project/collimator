# Confirm PASS — a67fe35a32185861 on `filegroups/source`

Cycle `20260526T032213-confirm-a67fe35a32185861` — 2026-05-26T03:22:13Z

PR_AUC held across 3 seeds (orig 0.9988)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a67fe35a32185861` | `f49eb3ae5c8f1e97` | `f49eb3ae5c8f1e97` | `f49eb3ae5c8f1e97` |
| PR AUC | 0.9988 | 0.9992 | 0.9992 | 0.9992 |
| ROC AUC | 0.9982 | 0.9985 | 0.9985 | 0.9986 |
| Recall@3FPM | — | 0.9162 | 0.9307 | 0.9159 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a67fe35a32185861
```
