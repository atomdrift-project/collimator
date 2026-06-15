# Confirm PASS — fa684a1ee61f2dbe on `filetypes/macho`

Cycle `20260614T234010-confirm-fa684a1ee61f2dbe` — 2026-06-14T23:40:10Z

PR_AUC held across 3 seeds (orig 0.9970)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `fa684a1ee61f2dbe` | `a7e007c50873c773` | `a7e007c50873c773` | `a7e007c50873c773` |
| PR AUC | 0.9970 | 0.9971 | 0.9974 | 0.9958 |
| ROC AUC | 0.9994 | 0.9994 | 0.9994 | 0.9990 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=fa684a1ee61f2dbe
```
