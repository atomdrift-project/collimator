# Confirm PASS — e862cf75d37e0f3b on `filetypes/macho`

Cycle `20260526T224150-confirm-e862cf75d37e0f3b` — 2026-05-26T22:41:50Z

PR_AUC held across 3 seeds (orig 0.9995)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e862cf75d37e0f3b` | `36d370bb4e062c39` | `36d370bb4e062c39` | `36d370bb4e062c39` |
| PR AUC | 0.9995 | 0.9971 | 0.9973 | 0.9968 |
| ROC AUC | 0.9999 | 0.9994 | 0.9994 | 0.9994 |
| Recall@3FPM | — | 0.8571 | 0.8947 | 0.7744 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e862cf75d37e0f3b
```
