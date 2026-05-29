# Confirm PASS — 32c6307be0ee939c on `filetypes/python-bytecode`

Cycle `20260526T225620-confirm-32c6307be0ee939c` — 2026-05-26T22:56:20Z

PR_AUC held across 3 seeds (orig 0.9988)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `32c6307be0ee939c` | `9f2d69804bd4c65f` | `9f2d69804bd4c65f` | `9f2d69804bd4c65f` |
| PR AUC | 0.9988 | 0.9981 | 0.9978 | 0.9981 |
| ROC AUC | 0.9923 | 0.9918 | 0.9911 | 0.9920 |
| Recall@3FPM | — | 0.9020 | 0.8367 | 0.8939 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=32c6307be0ee939c
```
