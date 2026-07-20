# Confirm PASS — f5114a9fbdb9aeed on `filetypes/php`

Cycle `20260718T142524-confirm-f5114a9fbdb9aeed` — 2026-07-18T14:25:24Z

PR_AUC held across 3 seeds (orig 0.9848)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f5114a9fbdb9aeed` | `3902d3b45076eddd` | `3902d3b45076eddd` | `3902d3b45076eddd` |
| PR AUC | 0.9848 | 0.9835 | 0.9856 | 0.9841 |
| ROC AUC | 0.9960 | 0.9955 | 0.9961 | 0.9952 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f5114a9fbdb9aeed
```
