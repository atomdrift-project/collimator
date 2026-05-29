# Confirm PASS — 84f9dd5f3bc20138 on `filetypes/lua`

Cycle `20260527T051759-confirm-84f9dd5f3bc20138` — 2026-05-27T05:17:59Z

PR_AUC held across 3 seeds (orig 0.5995)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `84f9dd5f3bc20138` | `90ec8d1435351d83` | `90ec8d1435351d83` | `90ec8d1435351d83` |
| PR AUC | 0.5995 | 0.7183 | 0.7088 | 0.7056 |
| ROC AUC | 0.7772 | 0.9076 | 0.8424 | 0.8641 |
| Recall@3FPM | — | 0.5000 | 0.5000 | 0.5000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=84f9dd5f3bc20138
```
