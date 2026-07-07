# Confirm PASS — 88bd6ca1bafd0168 on `filetypes/python`

Cycle `20260706T062607-confirm-88bd6ca1bafd0168` — 2026-07-06T06:26:07Z

PR_AUC held across 3 seeds (orig 0.9758)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `88bd6ca1bafd0168` | `333db9097d6103a5` | `333db9097d6103a5` | `333db9097d6103a5` |
| PR AUC | 0.9758 | 0.9791 | 0.9801 | 0.9797 |
| ROC AUC | 0.9882 | 0.9897 | 0.9902 | 0.9900 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=88bd6ca1bafd0168
```
