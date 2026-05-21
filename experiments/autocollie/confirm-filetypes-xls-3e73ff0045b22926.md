# Confirm PASS — 3e73ff0045b22926 on `filetypes/xls`

Cycle `20260520T194920-confirm-3e73ff0045b22926` — 2026-05-20T19:49:20Z

PR_AUC held across 3 seeds (orig 0.9992)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3e73ff0045b22926` | `cf6fc1d9f1dea005` | `cf6fc1d9f1dea005` | `cf6fc1d9f1dea005` |
| PR AUC | 0.9992 | 0.9992 | 0.9992 | 0.9992 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3e73ff0045b22926
```
