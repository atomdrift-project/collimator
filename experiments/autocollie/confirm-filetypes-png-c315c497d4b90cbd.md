# Confirm PASS — c315c497d4b90cbd on `filetypes/png`

Cycle `20260527T002651-confirm-c315c497d4b90cbd` — 2026-05-27T00:26:51Z

PR_AUC held across 3 seeds (orig 0.9822)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c315c497d4b90cbd` | `f1db21a6b0b28761` | `f1db21a6b0b28761` | `f1db21a6b0b28761` |
| PR AUC | 0.9822 | 0.9698 | 0.9812 | 0.9819 |
| ROC AUC | 0.9648 | 0.9496 | 0.9619 | 0.9630 |
| Recall@3FPM | — | 0.9231 | 0.9231 | 0.9231 |
| verdict | — | FAIL | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=c315c497d4b90cbd
```
