# Confirm PASS — 601bf6e22ee6fdf1 on `filetypes/zst`

Cycle `20260526T185041-confirm-601bf6e22ee6fdf1` — 2026-05-26T18:50:41Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `601bf6e22ee6fdf1` | `fe7cce089b5e9de8` | `fe7cce089b5e9de8` | `fe7cce089b5e9de8` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 1.0000 | 1.0000 | 1.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=601bf6e22ee6fdf1
```
