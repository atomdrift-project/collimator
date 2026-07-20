# Confirm PASS — 86a66667c2903d5d on `filetypes/pe`

Cycle `20260711T003741-confirm-86a66667c2903d5d` — 2026-07-11T00:37:41Z

PR_AUC held across 3 seeds (orig 0.9991)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `86a66667c2903d5d` | `6d46d5def8486008` | `6d46d5def8486008` | `6d46d5def8486008` |
| PR AUC | 0.9991 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9992 | 0.9998 | 0.9998 | 0.9998 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=86a66667c2903d5d
```
