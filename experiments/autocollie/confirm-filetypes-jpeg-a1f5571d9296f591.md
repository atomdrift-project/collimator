# Confirm PASS — a1f5571d9296f591 on `filetypes/jpeg`

Cycle `20260602T030739-confirm-a1f5571d9296f591` — 2026-06-02T03:07:39Z

PR_AUC held across 3 seeds (orig 0.9399)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a1f5571d9296f591` | `0ecdd05ad39583e1` | `0ecdd05ad39583e1` | `0ecdd05ad39583e1` |
| PR AUC | 0.9399 | 0.9752 | 0.9419 | 0.9787 |
| ROC AUC | 0.9683 | 0.9871 | 0.9699 | 0.9883 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a1f5571d9296f591
```
