# Confirm PASS — 45356b4891b0e539 on `filetypes/applescript`

Cycle `20260525T201823-confirm-45356b4891b0e539` — 2026-05-25T20:18:23Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `45356b4891b0e539` | `839a7e4c27ac4b33` | `839a7e4c27ac4b33` | `839a7e4c27ac4b33` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 1.0000 | 1.0000 | 1.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=45356b4891b0e539
```
