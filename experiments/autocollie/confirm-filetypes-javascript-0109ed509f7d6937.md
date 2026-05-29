# Confirm PASS — 0109ed509f7d6937 on `filetypes/javascript`

Cycle `20260525T161328-confirm-0109ed509f7d6937` — 2026-05-25T16:13:28Z

PR_AUC held across 3 seeds (orig 0.9993)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0109ed509f7d6937` | `ad25eb0dfbc4d7b6` | `ad25eb0dfbc4d7b6` | `ad25eb0dfbc4d7b6` |
| PR AUC | 0.9993 | 0.9997 | 0.9997 | 0.9996 |
| ROC AUC | 0.9990 | 0.9995 | 0.9995 | 0.9994 |
| Recall@3FPM | — | 0.8626 | 0.8310 | 0.8721 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0109ed509f7d6937
```
