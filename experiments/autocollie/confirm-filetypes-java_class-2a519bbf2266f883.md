# Confirm PASS — 2a519bbf2266f883 on `filetypes/java_class`

Cycle `20260526T191531-confirm-2a519bbf2266f883` — 2026-05-26T19:15:31Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `2a519bbf2266f883` | `9cd351918bb1eb5e` | `9cd351918bb1eb5e` | `9cd351918bb1eb5e` |
| PR AUC | 1.0000 | 0.9936 | 0.9966 | 0.9953 |
| ROC AUC | 1.0000 | 0.9985 | 0.9992 | 0.9988 |
| Recall@3FPM | — | 0.6467 | 0.8667 | 0.7333 |
| verdict | — | FAIL | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=2a519bbf2266f883
```
