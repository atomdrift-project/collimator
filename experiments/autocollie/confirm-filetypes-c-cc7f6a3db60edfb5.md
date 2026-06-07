# Confirm PASS — cc7f6a3db60edfb5 on `filetypes/c`

Cycle `20260606T152847-confirm-cc7f6a3db60edfb5` — 2026-06-06T15:28:47Z

PR_AUC held across 3 seeds (orig 0.9898)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `cc7f6a3db60edfb5` | `298ad3fcb7a39f6b` | `298ad3fcb7a39f6b` | `298ad3fcb7a39f6b` |
| PR AUC | 0.9898 | 0.9884 | 0.9869 | 0.9877 |
| ROC AUC | 0.9944 | 0.9951 | 0.9945 | 0.9947 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=cc7f6a3db60edfb5
```
