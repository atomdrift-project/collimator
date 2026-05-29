# Confirm PASS — 97d28d988e99a59b on `filetypes/batch`

Cycle `20260526T222829-confirm-97d28d988e99a59b` — 2026-05-26T22:28:29Z

PR_AUC held across 3 seeds (orig 0.9998)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `97d28d988e99a59b` | `16974a6869afdd53` | `16974a6869afdd53` | `16974a6869afdd53` |
| PR AUC | 0.9998 | 0.9995 | 0.9996 | 0.9995 |
| ROC AUC | 0.9983 | 0.9958 | 0.9962 | 0.9955 |
| Recall@3FPM | — | 0.9634 | 0.9817 | 0.9791 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=97d28d988e99a59b
```
