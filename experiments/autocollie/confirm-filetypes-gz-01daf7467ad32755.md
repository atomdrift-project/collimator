# Confirm PASS — 01daf7467ad32755 on `filetypes/gz`

Cycle `20260614T233337-confirm-01daf7467ad32755` — 2026-06-14T23:33:37Z

PR_AUC held across 3 seeds (orig 0.7119)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `01daf7467ad32755` | `027d0ab6cfa7c998` | `027d0ab6cfa7c998` | `027d0ab6cfa7c998` |
| PR AUC | 0.7119 | 0.7138 | 0.7250 | 0.7251 |
| ROC AUC | 0.8869 | 0.8927 | 0.8922 | 0.8813 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=01daf7467ad32755
```
