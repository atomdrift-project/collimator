# Confirm PASS — 1641548e327aaf0b on `filetypes/vbs`

Cycle `20260616T091458-confirm-1641548e327aaf0b` — 2026-06-16T09:14:58Z

PR_AUC held across 3 seeds (orig 0.9977)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `1641548e327aaf0b` | `5cfb4136ac594a38` | `5cfb4136ac594a38` | `5cfb4136ac594a38` |
| PR AUC | 0.9977 | 0.9976 | 0.9968 | 0.9968 |
| ROC AUC | 0.9926 | 0.9920 | 0.9899 | 0.9897 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=1641548e327aaf0b
```
