# Confirm PASS — bb868fdc18fa7fa4 on `filetypes/java_class`

Cycle `20260520T061016-confirm-bb868fdc18fa7fa4` — 2026-05-20T06:10:16Z

PR_AUC held across 3 seeds (orig 0.9969)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `bb868fdc18fa7fa4` | `af88f1c56d61ae0a` | `af88f1c56d61ae0a` | `af88f1c56d61ae0a` |
| PR AUC | 0.9969 | 0.9927 | 0.9958 | 0.9969 |
| ROC AUC | 0.9992 | 0.9984 | 0.9990 | 0.9992 |
| Recall@3FPM | — | 0.5400 | 0.7533 | 0.8733 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=bb868fdc18fa7fa4
```
