# Confirm PASS — 0bf19f66b3e1a2f2 on `filetypes/msi`

Cycle `20260514T164103-confirm-0bf19f66b3e1a2f2` — 2026-05-14T16:41:03Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0bf19f66b3e1a2f2` | `1547b4e8d80f09a8` | `1547b4e8d80f09a8` | `1547b4e8d80f09a8` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 1.0000 | 1.0000 | 1.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0bf19f66b3e1a2f2
```
