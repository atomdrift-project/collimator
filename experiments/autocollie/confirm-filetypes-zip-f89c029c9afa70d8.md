# Confirm PASS — f89c029c9afa70d8 on `filetypes/zip`

Cycle `20260613T231332-confirm-f89c029c9afa70d8` — 2026-06-13T23:13:32Z

PR_AUC held across 3 seeds (orig 0.9997)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f89c029c9afa70d8` | `f3fe11d1e4280c98` | `f3fe11d1e4280c98` | `f3fe11d1e4280c98` |
| PR AUC | 0.9997 | 0.9994 | 0.9994 | 0.9995 |
| ROC AUC | 0.9958 | 0.9947 | 0.9948 | 0.9953 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f89c029c9afa70d8
```
