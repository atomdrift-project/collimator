# Confirm PASS — fef3a5f7bf54badd on `filetypes/pe`

Cycle `20260703T044048-confirm-fef3a5f7bf54badd` — 2026-07-03T04:40:48Z

PR_AUC held across 3 seeds (orig 0.9983)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `fef3a5f7bf54badd` | `055c6f444bbbf55f` | `055c6f444bbbf55f` | `055c6f444bbbf55f` |
| PR AUC | 0.9983 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9984 | 0.9993 | 0.9993 | 0.9993 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=fef3a5f7bf54badd
```
