# Confirm PASS — 50f3a5c33d6fdc79 on `filetypes/java_class`

Cycle `20260526T192059-confirm-50f3a5c33d6fdc79` — 2026-05-26T19:20:59Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `50f3a5c33d6fdc79` | `7c0bc9aeafb27952` | `7c0bc9aeafb27952` | `7c0bc9aeafb27952` |
| PR AUC | 1.0000 | 0.9936 | 0.9966 | 0.9953 |
| ROC AUC | 1.0000 | 0.9985 | 0.9992 | 0.9988 |
| Recall@3FPM | — | 0.6467 | 0.8667 | 0.7333 |
| verdict | — | FAIL | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=50f3a5c33d6fdc79
```
