# Confirm PASS — 7edbe467b2c6f888 on `filetypes/javascript`

Cycle `20260526T073257-confirm-7edbe467b2c6f888` — 2026-05-26T07:32:57Z

PR_AUC held across 3 seeds (orig 0.9993)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `7edbe467b2c6f888` | `c7917fd92d5567bb` | `c7917fd92d5567bb` | `c7917fd92d5567bb` |
| PR AUC | 0.9993 | 0.9997 | 0.9997 | 0.9996 |
| ROC AUC | 0.9990 | 0.9995 | 0.9995 | 0.9995 |
| Recall@3FPM | — | 0.8870 | 0.8882 | 0.9046 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=7edbe467b2c6f888
```
