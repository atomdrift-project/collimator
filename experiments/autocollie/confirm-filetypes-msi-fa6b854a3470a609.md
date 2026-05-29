# Confirm PASS — fa6b854a3470a609 on `filetypes/msi`

Cycle `20260526T220008-confirm-fa6b854a3470a609` — 2026-05-26T22:00:08Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `fa6b854a3470a609` | `2eadbf9655aa6ade` | `2eadbf9655aa6ade` | `2eadbf9655aa6ade` |
| PR AUC | 0.9999 | 0.9993 | 0.9997 | 0.9997 |
| ROC AUC | 0.9990 | 0.9787 | 0.9912 | 0.9915 |
| Recall@3FPM | — | 0.8600 | 0.9567 | 0.9700 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=fa6b854a3470a609
```
