# Confirm PASS — 7a0f77dc39c615f0 on `filetypes/deb`

Cycle `20260525T200933-confirm-7a0f77dc39c615f0` — 2026-05-25T20:09:33Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `7a0f77dc39c615f0` | `43fb7f557dc31f57` | `43fb7f557dc31f57` | `43fb7f557dc31f57` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 1.0000 | 1.0000 | 1.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=7a0f77dc39c615f0
```
