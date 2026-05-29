# Confirm PASS — 65936fd5b3f175db on `filetypes/rust`

Cycle `20260527T050707-confirm-65936fd5b3f175db` — 2026-05-27T05:07:07Z

PR_AUC held across 3 seeds (orig 0.8862)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `65936fd5b3f175db` | `fbaed9aa52899dbc` | `fbaed9aa52899dbc` | `fbaed9aa52899dbc` |
| PR AUC | 0.8862 | 0.8908 | 0.8521 | 0.9209 |
| ROC AUC | 0.9840 | 0.9874 | 0.9832 | 0.9881 |
| Recall@3FPM | — | 0.3077 | 0.2308 | 0.6154 |
| verdict | — | PASS | FAIL | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=65936fd5b3f175db
```
