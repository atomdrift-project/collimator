# Confirm PASS — c8d99040e46f7dc4 on `filetypes/github-actions`

Cycle `20260527T054649-confirm-c8d99040e46f7dc4` — 2026-05-27T05:46:49Z

PR_AUC held across 3 seeds (orig 0.0037)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c8d99040e46f7dc4` | `3c9fb2016f5140f3` | `3c9fb2016f5140f3` | `3c9fb2016f5140f3` |
| PR AUC | 0.0037 | 0.0043 | 0.0043 | 0.0043 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=c8d99040e46f7dc4
```
