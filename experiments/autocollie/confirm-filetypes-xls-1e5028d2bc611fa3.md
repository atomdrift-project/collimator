# Confirm PASS — 1e5028d2bc611fa3 on `filetypes/xls`

Cycle `20260525T182239-confirm-1e5028d2bc611fa3` — 2026-05-25T18:22:39Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `1e5028d2bc611fa3` | `f97561ef4fd2772c` | `f97561ef4fd2772c` | `f97561ef4fd2772c` |
| PR AUC | 0.9999 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9995 | 0.9995 | 0.9995 | 0.9995 |
| Recall@3FPM | — | 0.9894 | 0.9902 | 0.9894 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=1e5028d2bc611fa3
```
