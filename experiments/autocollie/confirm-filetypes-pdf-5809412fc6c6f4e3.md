# Confirm PASS — 5809412fc6c6f4e3 on `filetypes/pdf`

Cycle `20260721T072619-confirm-5809412fc6c6f4e3` — 2026-07-21T07:26:19Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `5809412fc6c6f4e3` | `f82ebfbc3990abd4` | `f82ebfbc3990abd4` | `f82ebfbc3990abd4` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9991 | 0.9991 | 0.9992 | 0.9986 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=5809412fc6c6f4e3
```
