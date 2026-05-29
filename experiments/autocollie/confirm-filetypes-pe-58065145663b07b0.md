# Confirm PASS — 58065145663b07b0 on `filetypes/pe`

Cycle `20260526T091013-confirm-58065145663b07b0` — 2026-05-26T09:10:13Z

PR_AUC held across 3 seeds (orig 0.9997)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `58065145663b07b0` | `e9c183a44de3d1b8` | `e9c183a44de3d1b8` | `e9c183a44de3d1b8` |
| PR AUC | 0.9997 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9997 | 0.9999 | 0.9999 | 0.9999 |
| Recall@3FPM | — | 0.8110 | 0.8121 | 0.8368 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=58065145663b07b0
```
