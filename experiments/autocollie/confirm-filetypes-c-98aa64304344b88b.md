# Confirm PASS — 98aa64304344b88b on `filetypes/c`

Cycle `20260514T131409-confirm-98aa64304344b88b` — 2026-05-14T13:14:09Z

PR_AUC held across 3 seeds (orig 0.9997)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `98aa64304344b88b` | `13e5046cd24f8229` | `13e5046cd24f8229` | `13e5046cd24f8229` |
| PR AUC | 0.9997 | 0.9994 | 0.9996 | 0.9994 |
| ROC AUC | 0.9998 | 0.9997 | 0.9998 | 0.9997 |
| Recall@3FPM | — | 0.9369 | 0.9509 | 0.8598 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=98aa64304344b88b
```
