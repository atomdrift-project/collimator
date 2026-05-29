# Confirm PASS — 773e5f833a6f2326 on `filetypes/java_class`

Cycle `20260526T193024-confirm-773e5f833a6f2326` — 2026-05-26T19:30:24Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `773e5f833a6f2326` | `57a0ddd7b9740c66` | `57a0ddd7b9740c66` | `57a0ddd7b9740c66` |
| PR AUC | 1.0000 | 0.9964 | 0.9965 | 0.9965 |
| ROC AUC | 1.0000 | 0.9991 | 0.9992 | 0.9991 |
| Recall@3FPM | — | 0.8067 | 0.7800 | 0.8400 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=773e5f833a6f2326
```
