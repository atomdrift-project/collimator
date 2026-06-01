# Confirm PASS — 6c4ccd5e0b19dbbe on `filetypes/pe`

Cycle `20260601T164113-confirm-6c4ccd5e0b19dbbe` — 2026-06-01T16:41:13Z

PR_AUC held across 3 seeds (orig 0.9995)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6c4ccd5e0b19dbbe` | `1606da98452f4d08` | `1606da98452f4d08` | `1606da98452f4d08` |
| PR AUC | 0.9995 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9995 | 0.9999 | 0.9999 | 0.9999 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=6c4ccd5e0b19dbbe
```
