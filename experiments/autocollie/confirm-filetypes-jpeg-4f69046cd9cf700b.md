# Confirm PASS — 4f69046cd9cf700b on `filetypes/jpeg`

Cycle `20260617T174721-confirm-4f69046cd9cf700b` — 2026-06-17T17:47:21Z

PR_AUC held across 3 seeds (orig 0.9879)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `4f69046cd9cf700b` | `cbad697ad93ac53d` | `cbad697ad93ac53d` | `cbad697ad93ac53d` |
| PR AUC | 0.9879 | 0.9880 | 0.9807 | 0.9811 |
| ROC AUC | 0.9930 | 0.9940 | 0.9898 | 0.9898 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | FAIL | FAIL |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=4f69046cd9cf700b
```
