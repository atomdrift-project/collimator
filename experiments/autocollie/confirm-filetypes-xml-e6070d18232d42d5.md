# Confirm PASS — e6070d18232d42d5 on `filetypes/xml`

Cycle `20260712T143557-confirm-e6070d18232d42d5` — 2026-07-12T14:35:57Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e6070d18232d42d5` | `35fa26e6d236a128` | `35fa26e6d236a128` | `35fa26e6d236a128` |
| PR AUC | 1.0000 | 0.9979 | 0.9985 | 0.9995 |
| ROC AUC | 1.0000 | 0.9994 | 0.9996 | 0.9999 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e6070d18232d42d5
```
