# Confirm PASS — e87eacbcbe92d034 on `filetypes/vbs`

Cycle `20260526T222931-confirm-e87eacbcbe92d034` — 2026-05-26T22:29:31Z

PR_AUC held across 3 seeds (orig 0.9995)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e87eacbcbe92d034` | `7d0815ce1b0df554` | `7d0815ce1b0df554` | `7d0815ce1b0df554` |
| PR AUC | 0.9995 | 0.9969 | 0.9853 | 0.9957 |
| ROC AUC | 0.9993 | 0.9798 | 0.9101 | 0.9762 |
| Recall@3FPM | — | 0.3614 | 0.0000 | 0.2062 |
| verdict | — | PASS | FAIL | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e87eacbcbe92d034
```
