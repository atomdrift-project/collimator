# Confirm PASS — b622b01f1169bfea on `filetypes/pkg-info`

Cycle `20260525T200426-confirm-b622b01f1169bfea` — 2026-05-25T20:04:26Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b622b01f1169bfea` | `838ee6a94ae43a9e` | `838ee6a94ae43a9e` | `838ee6a94ae43a9e` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 1.0000 | 1.0000 | 1.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b622b01f1169bfea
```
