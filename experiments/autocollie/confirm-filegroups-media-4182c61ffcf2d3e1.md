# Confirm PASS — 4182c61ffcf2d3e1 on `filegroups/media`

Cycle `20260515T085105-confirm-4182c61ffcf2d3e1` — 2026-05-15T08:51:05Z

PR_AUC held across 3 seeds (orig 0.9984)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `4182c61ffcf2d3e1` | `c447db0409f38c12` | `c447db0409f38c12` | `c447db0409f38c12` |
| PR AUC | 0.9984 | 0.9976 | 0.9948 | 0.9988 |
| ROC AUC | 0.9982 | 0.9973 | 0.9925 | 0.9986 |
| Recall@3FPM | — | 0.8816 | 0.9474 | 0.9079 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=4182c61ffcf2d3e1
```
