# Confirm PASS — 21df9b94706f0054 on `filetypes/pdf`

Cycle `20260715T035637-confirm-21df9b94706f0054` — 2026-07-15T03:56:37Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `21df9b94706f0054` | `89b7c8bfd947c678` | `89b7c8bfd947c678` | `89b7c8bfd947c678` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 0.9999 |
| ROC AUC | 0.9995 | 0.9991 | 0.9992 | 0.9930 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=21df9b94706f0054
```
