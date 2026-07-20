# Confirm PASS — e71f5601bfa41eb2 on `filetypes/whl`

Cycle `20260713T214852-confirm-e71f5601bfa41eb2` — 2026-07-13T21:48:52Z

PR_AUC held across 3 seeds (orig 0.9690)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e71f5601bfa41eb2` | `e2c2054d962de0eb` | `e2c2054d962de0eb` | `e2c2054d962de0eb` |
| PR AUC | 0.9690 | 0.9681 | 0.9674 | 0.9699 |
| ROC AUC | 0.9678 | 0.9669 | 0.9651 | 0.9688 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e71f5601bfa41eb2
```
