# Confirm PASS — 65f71553d88b8f51 on `filetypes/shell`

Cycle `20260704T081011-confirm-65f71553d88b8f51` — 2026-07-04T08:10:11Z

PR_AUC held across 3 seeds (orig 0.9949)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `65f71553d88b8f51` | `0dae45d16790bc4a` | `0dae45d16790bc4a` | `0dae45d16790bc4a` |
| PR AUC | 0.9949 | 0.9924 | 0.9918 | 0.9925 |
| ROC AUC | 0.9966 | 0.9943 | 0.9937 | 0.9943 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=65f71553d88b8f51
```
