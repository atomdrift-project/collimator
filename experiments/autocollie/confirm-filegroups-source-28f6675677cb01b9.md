# Confirm PASS — 28f6675677cb01b9 on `filegroups/source`

Cycle `20260525T153007-confirm-28f6675677cb01b9` — 2026-05-25T15:30:07Z

PR_AUC held across 3 seeds (orig 0.9989)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `28f6675677cb01b9` | `cd5b1f975b5d4960` | `cd5b1f975b5d4960` | `cd5b1f975b5d4960` |
| PR AUC | 0.9989 | 0.9991 | 0.9991 | 0.9991 |
| ROC AUC | 0.9982 | 0.9983 | 0.9983 | 0.9984 |
| Recall@3FPM | — | 0.9184 | 0.9450 | 0.9275 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=28f6675677cb01b9
```
