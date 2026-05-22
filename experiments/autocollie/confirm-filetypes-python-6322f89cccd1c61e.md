# Confirm PASS — 6322f89cccd1c61e on `filetypes/python`

Cycle `20260522T164747-confirm-6322f89cccd1c61e` — 2026-05-22T16:47:47Z

PR_AUC held across 3 seeds (orig 0.9985)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6322f89cccd1c61e` | `664104eced8ff8a4` | `664104eced8ff8a4` | `664104eced8ff8a4` |
| PR AUC | 0.9985 | 0.9984 | 0.9982 | 0.9984 |
| ROC AUC | 0.9986 | 0.9986 | 0.9984 | 0.9986 |
| Recall@3FPM | — | 0.7991 | 0.7627 | 0.7381 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=6322f89cccd1c61e
```
