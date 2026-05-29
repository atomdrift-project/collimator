# Confirm PASS — c32d6213d911d26d on `filetypes/c`

Cycle `20260525T184040-confirm-c32d6213d911d26d` — 2026-05-25T18:40:40Z

PR_AUC held across 3 seeds (orig 0.9908)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c32d6213d911d26d` | `c690b23cd0ec7874` | `c690b23cd0ec7874` | `c690b23cd0ec7874` |
| PR AUC | 0.9908 | 0.9920 | 0.9913 | 0.9918 |
| ROC AUC | 0.9951 | 0.9958 | 0.9953 | 0.9956 |
| Recall@3FPM | — | 0.8009 | 0.7801 | 0.7963 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=c32d6213d911d26d
```
