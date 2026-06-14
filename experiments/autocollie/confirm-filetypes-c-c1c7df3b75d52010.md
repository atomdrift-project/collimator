# Confirm PASS — c1c7df3b75d52010 on `filetypes/c`

Cycle `20260614T020855-confirm-c1c7df3b75d52010` — 2026-06-14T02:08:55Z

PR_AUC held across 3 seeds (orig 0.9862)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c1c7df3b75d52010` | `fc2368a04386633a` | `fc2368a04386633a` | `fc2368a04386633a` |
| PR AUC | 0.9862 | 0.9837 | 0.9840 | 0.9843 |
| ROC AUC | 0.9939 | 0.9928 | 0.9927 | 0.9933 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=c1c7df3b75d52010
```
