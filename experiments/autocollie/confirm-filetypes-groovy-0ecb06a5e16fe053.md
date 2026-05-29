# Confirm PASS — 0ecb06a5e16fe053 on `filetypes/groovy`

Cycle `20260527T075711-confirm-0ecb06a5e16fe053` — 2026-05-27T07:57:11Z

PR_AUC held across 3 seeds (orig 0.6667)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0ecb06a5e16fe053` | `5605092150b37dac` | `5605092150b37dac` | `5605092150b37dac` |
| PR AUC | 0.6667 | 0.6667 | 0.6667 | 0.6667 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0ecb06a5e16fe053
```
