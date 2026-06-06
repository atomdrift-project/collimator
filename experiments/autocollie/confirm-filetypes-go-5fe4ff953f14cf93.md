# Confirm PASS — 5fe4ff953f14cf93 on `filetypes/go`

Cycle `20260606T110812-confirm-5fe4ff953f14cf93` — 2026-06-06T11:08:12Z

PR_AUC held across 3 seeds (orig 0.9439)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `5fe4ff953f14cf93` | `063082f772286a7d` | `063082f772286a7d` | `063082f772286a7d` |
| PR AUC | 0.9439 | 0.9401 | 0.9430 | 0.9478 |
| ROC AUC | 0.9862 | 0.9846 | 0.9849 | 0.9862 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=5fe4ff953f14cf93
```
