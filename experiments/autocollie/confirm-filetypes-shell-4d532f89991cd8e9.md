# Confirm PASS — 4d532f89991cd8e9 on `filetypes/shell`

Cycle `20260715T092356-confirm-4d532f89991cd8e9` — 2026-07-15T09:23:56Z

PR_AUC held across 3 seeds (orig 0.9908)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `4d532f89991cd8e9` | `8699691ae3fd18d6` | `8699691ae3fd18d6` | `8699691ae3fd18d6` |
| PR AUC | 0.9908 | 0.9909 | 0.9914 | 0.9915 |
| ROC AUC | 0.9948 | 0.9946 | 0.9949 | 0.9948 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=4d532f89991cd8e9
```
