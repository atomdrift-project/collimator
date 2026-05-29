# Confirm PASS — 13a69eff3b5b3242 on `filetypes/java_class`

Cycle `20260525T195511-confirm-13a69eff3b5b3242` — 2026-05-25T19:55:11Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `13a69eff3b5b3242` | `f3a0042bd5bfd071` | `f3a0042bd5bfd071` | `f3a0042bd5bfd071` |
| PR AUC | 1.0000 | 0.9942 | 0.9966 | 0.9953 |
| ROC AUC | 1.0000 | 0.9986 | 0.9992 | 0.9988 |
| Recall@3FPM | — | 0.7467 | 0.8667 | 0.7333 |
| verdict | — | FAIL | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=13a69eff3b5b3242
```
