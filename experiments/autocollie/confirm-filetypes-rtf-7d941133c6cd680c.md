# Confirm PASS — 7d941133c6cd680c on `filetypes/rtf`

Cycle `20260712T151236-confirm-7d941133c6cd680c` — 2026-07-12T15:12:36Z

PR_AUC held across 3 seeds (orig 0.9996)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `7d941133c6cd680c` | `18057a4c28c7f1b3` | `18057a4c28c7f1b3` | `18057a4c28c7f1b3` |
| PR AUC | 0.9996 | 0.9997 | 0.9996 | 0.9995 |
| ROC AUC | 0.9978 | 0.9985 | 0.9982 | 0.9978 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=7d941133c6cd680c
```
