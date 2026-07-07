# Confirm PASS — c1961897e0f037de on `filetypes/c`

Cycle `20260706T055024-confirm-c1961897e0f037de` — 2026-07-06T05:50:24Z

PR_AUC held across 3 seeds (orig 0.9749)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c1961897e0f037de` | `c427b1bdaaa8148b` | `c427b1bdaaa8148b` | `c427b1bdaaa8148b` |
| PR AUC | 0.9749 | 0.9751 | 0.9761 | 0.9742 |
| ROC AUC | 0.9914 | 0.9904 | 0.9921 | 0.9918 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=c1961897e0f037de
```
