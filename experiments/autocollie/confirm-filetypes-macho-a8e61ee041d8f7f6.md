# Confirm PASS — a8e61ee041d8f7f6 on `filetypes/macho`

Cycle `20260526T223429-confirm-a8e61ee041d8f7f6` — 2026-05-26T22:34:29Z

PR_AUC held across 3 seeds (orig 0.9996)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a8e61ee041d8f7f6` | `41b2f28cc2e4106f` | `41b2f28cc2e4106f` | `41b2f28cc2e4106f` |
| PR AUC | 0.9996 | 0.9972 | 0.9974 | 0.9969 |
| ROC AUC | 0.9999 | 0.9994 | 0.9994 | 0.9994 |
| Recall@3FPM | — | 0.8609 | 0.9023 | 0.7669 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a8e61ee041d8f7f6
```
