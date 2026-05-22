# Confirm PASS — 9664e37df073f080 on `filetypes/java_class`

Cycle `20260522T171614-confirm-9664e37df073f080` — 2026-05-22T17:16:14Z

PR_AUC held across 3 seeds (orig 0.9965)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `9664e37df073f080` | `06ede31238ca18dc` | `06ede31238ca18dc` | `06ede31238ca18dc` |
| PR AUC | 0.9965 | 0.9964 | 0.9946 | 0.9969 |
| ROC AUC | 0.9992 | 0.9991 | 0.9987 | 0.9992 |
| Recall@3FPM | — | 0.8067 | 0.8000 | 0.8533 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=9664e37df073f080
```
