# Confirm PASS — 9e970e68ddc80e09 on `filetypes/python`

Cycle `20260521T030114-confirm-9e970e68ddc80e09` — 2026-05-21T03:01:14Z

PR_AUC held across 3 seeds (orig 0.9986)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `9e970e68ddc80e09` | `dcd62ec815ee570e` | `dcd62ec815ee570e` | `dcd62ec815ee570e` |
| PR AUC | 0.9986 | 0.9986 | 0.9985 | 0.9986 |
| ROC AUC | 0.9988 | 0.9988 | 0.9987 | 0.9988 |
| Recall@3FPM | — | 0.8018 | 0.7911 | 0.8452 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=9e970e68ddc80e09
```
