# Confirm PASS — 22050bfdea649807 on `filetypes/vbs`

Cycle `20260712T123834-confirm-22050bfdea649807` — 2026-07-12T12:38:34Z

PR_AUC held across 3 seeds (orig 0.9998)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `22050bfdea649807` | `dd0a5383e2ec1806` | `dd0a5383e2ec1806` | `dd0a5383e2ec1806` |
| PR AUC | 0.9998 | 0.9998 | 0.9998 | 0.9982 |
| ROC AUC | 0.9972 | 0.9973 | 0.9970 | 0.9715 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=22050bfdea649807
```
