# Confirm PASS — 0fa84e4e3ec6ae7d on `filetypes/rtf`

Cycle `20260627T213111-confirm-0fa84e4e3ec6ae7d` — 2026-06-27T21:31:11Z

PR_AUC held across 3 seeds (orig 0.9998)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0fa84e4e3ec6ae7d` | `eeb7aa90f2c3d6c7` | `eeb7aa90f2c3d6c7` | `eeb7aa90f2c3d6c7` |
| PR AUC | 0.9998 | 0.9998 | 0.9997 | 0.9998 |
| ROC AUC | 0.9984 | 0.9984 | 0.9980 | 0.9984 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0fa84e4e3ec6ae7d
```
