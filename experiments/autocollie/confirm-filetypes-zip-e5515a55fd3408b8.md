# Confirm PASS — e5515a55fd3408b8 on `filetypes/zip`

Cycle `20260525T051700-confirm-e5515a55fd3408b8` — 2026-05-25T05:17:00Z

PR_AUC held across 3 seeds (orig 0.9998)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e5515a55fd3408b8` | `8b65d913d456d1cd` | `8b65d913d456d1cd` | `8b65d913d456d1cd` |
| PR AUC | 0.9998 | 0.9998 | 0.9998 | 0.9997 |
| ROC AUC | 0.9960 | 0.9959 | 0.9959 | 0.9955 |
| Recall@3FPM | — | 0.6856 | 0.6845 | 0.6950 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e5515a55fd3408b8
```
