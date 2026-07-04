# Confirm PASS — 04f53a576111ba93 on `filegroups/source`

Cycle `20260704T081000-confirm-04f53a576111ba93` — 2026-07-04T08:10:00Z

PR_AUC held across 3 seeds (orig 0.9990)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `04f53a576111ba93` | `66538b89b739a2bb` | `66538b89b739a2bb` | `66538b89b739a2bb` |
| PR AUC | 0.9990 | 0.9959 | 0.9959 | 0.9960 |
| ROC AUC | 0.9982 | 0.9963 | 0.9963 | 0.9964 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=04f53a576111ba93
```
