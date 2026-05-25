# Confirm PASS — a30b07f6d1a71ff0 on `filetypes/zst`

Cycle `20260525T081518-confirm-a30b07f6d1a71ff0` — 2026-05-25T08:15:18Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a30b07f6d1a71ff0` | `a1128cb74f008e36` | `a1128cb74f008e36` | `a1128cb74f008e36` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 1.0000 | 1.0000 | 1.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a30b07f6d1a71ff0
```
