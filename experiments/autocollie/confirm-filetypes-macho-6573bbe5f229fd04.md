# Confirm PASS — 6573bbe5f229fd04 on `filetypes/macho`

Cycle `20260614T234950-confirm-6573bbe5f229fd04` — 2026-06-14T23:49:50Z

PR_AUC held across 3 seeds (orig 0.9966)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6573bbe5f229fd04` | `5662706c39bf035f` | `5662706c39bf035f` | `5662706c39bf035f` |
| PR AUC | 0.9966 | 0.9971 | 0.9974 | 0.9958 |
| ROC AUC | 0.9993 | 0.9994 | 0.9994 | 0.9990 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=6573bbe5f229fd04
```
