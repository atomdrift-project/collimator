# Confirm PASS — 19f0b2dd70564c54 on `filetypes/zip`

Cycle `20260628T125431-confirm-19f0b2dd70564c54` — 2026-06-28T12:54:31Z

PR_AUC held across 3 seeds (orig 0.9996)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `19f0b2dd70564c54` | `32fcd545116dc2df` | `32fcd545116dc2df` | `32fcd545116dc2df` |
| PR AUC | 0.9996 | 0.9997 | 0.9997 | 0.9996 |
| ROC AUC | 0.9973 | 0.9984 | 0.9982 | 0.9980 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=19f0b2dd70564c54
```
