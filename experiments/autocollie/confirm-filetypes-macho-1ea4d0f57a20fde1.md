# Confirm PASS — 1ea4d0f57a20fde1 on `filetypes/macho`

Cycle `20260601T211714-confirm-1ea4d0f57a20fde1` — 2026-06-01T21:17:14Z

PR_AUC held across 3 seeds (orig 0.9996)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `1ea4d0f57a20fde1` | `403527c9d5da874a` | `403527c9d5da874a` | `403527c9d5da874a` |
| PR AUC | 0.9996 | 0.9963 | 0.9959 | 0.9962 |
| ROC AUC | 0.9999 | 0.9991 | 0.9989 | 0.9991 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=1ea4d0f57a20fde1
```
