# Confirm PASS — a1631fc7b720c45a on `filetypes/powershell`

Cycle `20260526T230116-confirm-a1631fc7b720c45a` — 2026-05-26T23:01:16Z

PR_AUC held across 3 seeds (orig 0.9972)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a1631fc7b720c45a` | `7001795e80db74d0` | `7001795e80db74d0` | `7001795e80db74d0` |
| PR AUC | 0.9972 | 0.9987 | 0.9986 | 0.9968 |
| ROC AUC | 0.9990 | 0.9983 | 0.9981 | 0.9961 |
| Recall@3FPM | — | 0.8333 | 0.7869 | 0.6967 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a1631fc7b720c45a
```
