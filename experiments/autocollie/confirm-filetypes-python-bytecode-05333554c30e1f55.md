# Confirm PASS — 05333554c30e1f55 on `filetypes/python-bytecode`

Cycle `20260706T085539-confirm-05333554c30e1f55` — 2026-07-06T08:55:39Z

PR_AUC held across 3 seeds (orig 0.9948)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `05333554c30e1f55` | `60d7f35b1456b041` | `60d7f35b1456b041` | `60d7f35b1456b041` |
| PR AUC | 0.9948 | 0.9950 | 0.9947 | 0.9934 |
| ROC AUC | 0.9972 | 0.9979 | 0.9978 | 0.9969 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=05333554c30e1f55
```
