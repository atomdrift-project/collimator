# Confirm PASS — 75895df7f854c7cb on `filetypes/java_class`

Cycle `20260720T114105-confirm-75895df7f854c7cb` — 2026-07-20T11:41:05Z

PR_AUC held across 3 seeds (orig 0.9905)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `75895df7f854c7cb` | `c9488885127e4a4a` | `c9488885127e4a4a` | `c9488885127e4a4a` |
| PR AUC | 0.9905 | 0.9901 | 0.9885 | 0.9877 |
| ROC AUC | 0.9987 | 0.9986 | 0.9986 | 0.9984 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=75895df7f854c7cb
```
