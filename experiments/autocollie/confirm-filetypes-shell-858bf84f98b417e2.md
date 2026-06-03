# Confirm PASS — 858bf84f98b417e2 on `filetypes/shell`

Cycle `20260603T163548-confirm-858bf84f98b417e2` — 2026-06-03T16:35:48Z

PR_AUC held across 3 seeds (orig 0.9991)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `858bf84f98b417e2` | `6cdfa949aa04a7e6` | `6cdfa949aa04a7e6` | `6cdfa949aa04a7e6` |
| PR AUC | 0.9991 | 0.9990 | 0.9990 | 0.9991 |
| ROC AUC | 0.9991 | 0.9990 | 0.9990 | 0.9992 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=858bf84f98b417e2
```
