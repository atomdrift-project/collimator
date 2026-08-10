# Confirm PASS — 054275c39fad748a on `filetypes/tar`

Cycle `20260805T145630-confirm-054275c39fad748a` — 2026-08-05T14:56:30Z

PR_AUC held across 3 seeds (orig 0.9380)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `054275c39fad748a` | `022c927fcaca5b74` | `022c927fcaca5b74` | `022c927fcaca5b74` |
| PR AUC | 0.9380 | 0.9358 | 0.9354 | 0.9337 |
| ROC AUC | 0.9655 | 0.9625 | 0.9601 | 0.9612 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=054275c39fad748a
```
