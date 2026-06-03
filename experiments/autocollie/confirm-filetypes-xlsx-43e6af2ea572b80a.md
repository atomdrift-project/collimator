# Confirm PASS — 43e6af2ea572b80a on `filetypes/xlsx`

Cycle `20260603T163346-confirm-43e6af2ea572b80a` — 2026-06-03T16:33:46Z

PR_AUC held across 3 seeds (orig 0.9974)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `43e6af2ea572b80a` | `1c03c3ae4abc7fe3` | `1c03c3ae4abc7fe3` | `1c03c3ae4abc7fe3` |
| PR AUC | 0.9974 | 0.9974 | 0.9974 | 0.9974 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=43e6af2ea572b80a
```
