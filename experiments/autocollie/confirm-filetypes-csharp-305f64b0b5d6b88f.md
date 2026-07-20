# Confirm PASS — 305f64b0b5d6b88f on `filetypes/csharp`

Cycle `20260712T140245-confirm-305f64b0b5d6b88f` — 2026-07-12T14:02:45Z

PR_AUC held across 3 seeds (orig 0.9904)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `305f64b0b5d6b88f` | `ff3fba88cbef343a` | `ff3fba88cbef343a` | `ff3fba88cbef343a` |
| PR AUC | 0.9904 | 0.9894 | 0.9902 | 0.9896 |
| ROC AUC | 0.9971 | 0.9968 | 0.9971 | 0.9968 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=305f64b0b5d6b88f
```
