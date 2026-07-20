# Confirm PASS — aecb01bd106efdd5 on `filetypes/jar`

Cycle `20260711T141218-confirm-aecb01bd106efdd5` — 2026-07-11T14:12:18Z

PR_AUC held across 3 seeds (orig 0.9844)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `aecb01bd106efdd5` | `9388f031b7766db3` | `9388f031b7766db3` | `9388f031b7766db3` |
| PR AUC | 0.9844 | 0.9873 | 0.9861 | 0.9821 |
| ROC AUC | 0.9818 | 0.9856 | 0.9839 | 0.9791 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=aecb01bd106efdd5
```
