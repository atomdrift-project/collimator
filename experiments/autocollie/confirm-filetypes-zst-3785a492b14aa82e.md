# Confirm PASS — 3785a492b14aa82e on `filetypes/zst`

Cycle `20260525T194705-confirm-3785a492b14aa82e` — 2026-05-25T19:47:05Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3785a492b14aa82e` | `a40cd2094632acf8` | `a40cd2094632acf8` | `a40cd2094632acf8` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 1.0000 | 1.0000 | 1.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3785a492b14aa82e
```
