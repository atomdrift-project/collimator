# Confirm PASS — 8a98408e364fcb32 on `filetypes/xls`

Cycle `20260713T045818-confirm-8a98408e364fcb32` — 2026-07-13T04:58:18Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `8a98408e364fcb32` | `c684044438dffa23` | `c684044438dffa23` | `c684044438dffa23` |
| PR AUC | 0.9999 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9989 | 0.9990 | 0.9990 | 0.9990 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=8a98408e364fcb32
```
