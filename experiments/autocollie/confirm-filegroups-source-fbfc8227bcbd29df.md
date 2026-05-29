# Confirm PASS — fbfc8227bcbd29df on `filegroups/source`

Cycle `20260526T033133-confirm-fbfc8227bcbd29df` — 2026-05-26T03:31:33Z

PR_AUC held across 3 seeds (orig 0.9988)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `fbfc8227bcbd29df` | `67e067b1490da1f1` | `67e067b1490da1f1` | `67e067b1490da1f1` |
| PR AUC | 0.9988 | 0.9992 | 0.9992 | 0.9993 |
| ROC AUC | 0.9982 | 0.9985 | 0.9985 | 0.9986 |
| Recall@3FPM | — | 0.9278 | 0.9243 | 0.9246 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=fbfc8227bcbd29df
```
