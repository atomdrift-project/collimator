# Confirm PASS — 8b65fc59cb931213 on `filetypes/csharp`

Cycle `20260716T024914-confirm-8b65fc59cb931213` — 2026-07-16T02:49:14Z

PR_AUC held across 3 seeds (orig 0.9886)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `8b65fc59cb931213` | `800d94a8d32e0586` | `800d94a8d32e0586` | `800d94a8d32e0586` |
| PR AUC | 0.9886 | 0.9886 | 0.9903 | 0.9880 |
| ROC AUC | 0.9967 | 0.9967 | 0.9972 | 0.9964 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=8b65fc59cb931213
```
