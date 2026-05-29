# Confirm PASS — 1ea4d0f57a20fde1 on `filetypes/macho`

Cycle `20260526T223032-confirm-1ea4d0f57a20fde1` — 2026-05-26T22:30:32Z

PR_AUC held across 3 seeds (orig 0.9996)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `1ea4d0f57a20fde1` | `807df786f956b83d` | `807df786f956b83d` | `807df786f956b83d` |
| PR AUC | 0.9996 | 0.9974 | 0.9973 | 0.9972 |
| ROC AUC | 0.9999 | 0.9994 | 0.9994 | 0.9994 |
| Recall@3FPM | — | 0.8759 | 0.8835 | 0.8759 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=1ea4d0f57a20fde1
```
