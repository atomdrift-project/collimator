# Confirm PASS — d40309f64ea1f776 on `filetypes/xml`

Cycle `20260526T195844-confirm-d40309f64ea1f776` — 2026-05-26T19:58:44Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d40309f64ea1f776` | `09cb09ce34b14f81` | `09cb09ce34b14f81` | `09cb09ce34b14f81` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 1.0000 | 1.0000 | 1.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d40309f64ea1f776
```
