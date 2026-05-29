# Confirm PASS — 7dd6d50a2de2d5b8 on `filetypes/github-actions`

Cycle `20260525T213542-confirm-7dd6d50a2de2d5b8` — 2026-05-25T21:35:42Z

PR_AUC held across 3 seeds (orig 0.0037)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `7dd6d50a2de2d5b8` | `3c9fb2016f5140f3` | `3c9fb2016f5140f3` | `3c9fb2016f5140f3` |
| PR AUC | 0.0037 | 0.0043 | 0.0043 | 0.0043 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=7dd6d50a2de2d5b8
```
