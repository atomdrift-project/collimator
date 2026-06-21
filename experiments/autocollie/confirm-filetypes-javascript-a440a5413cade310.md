# Confirm PASS — a440a5413cade310 on `filetypes/javascript`

Cycle `20260618T022139-confirm-a440a5413cade310` — 2026-06-18T02:21:39Z

PR_AUC held across 3 seeds (orig 0.9975)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a440a5413cade310` | `76c87a9be457f8f6` | `76c87a9be457f8f6` | `76c87a9be457f8f6` |
| PR AUC | 0.9975 | 0.9990 | 0.9991 | 0.9990 |
| ROC AUC | 0.9968 | 0.9986 | 0.9987 | 0.9987 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a440a5413cade310
```
