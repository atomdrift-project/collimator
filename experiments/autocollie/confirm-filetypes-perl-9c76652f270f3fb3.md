# Confirm PASS — 9c76652f270f3fb3 on `filetypes/perl`

Cycle `20260521T022954-confirm-9c76652f270f3fb3` — 2026-05-21T02:29:54Z

PR_AUC held across 3 seeds (orig 0.9978)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `9c76652f270f3fb3` | `d65f0ce1ea65da7f` | `d65f0ce1ea65da7f` | `d65f0ce1ea65da7f` |
| PR AUC | 0.9978 | 0.9956 | 0.9857 | 0.9959 |
| ROC AUC | 0.9998 | 0.9996 | 0.9981 | 0.9996 |
| Recall@3FPM | — | 0.9048 | 0.9524 | 0.9524 |
| verdict | — | PASS | FAIL | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=9c76652f270f3fb3
```
