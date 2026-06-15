# Confirm PASS — 32ab2a277d74951e on `filetypes/python`

Cycle `20260615T063720-confirm-32ab2a277d74951e` — 2026-06-15T06:37:20Z

PR_AUC held across 3 seeds (orig 0.9912)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `32ab2a277d74951e` | `ec422ee060db7a98` | `ec422ee060db7a98` | `ec422ee060db7a98` |
| PR AUC | 0.9912 | 0.9920 | 0.9920 | 0.9920 |
| ROC AUC | 0.9936 | 0.9941 | 0.9940 | 0.9941 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=32ab2a277d74951e
```
