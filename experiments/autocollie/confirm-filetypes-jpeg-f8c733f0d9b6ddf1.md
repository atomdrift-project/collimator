# Confirm PASS — f8c733f0d9b6ddf1 on `filetypes/jpeg`

Cycle `20260520T073011-confirm-f8c733f0d9b6ddf1` — 2026-05-20T07:30:11Z

PR_AUC held across 3 seeds (orig 0.9798)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f8c733f0d9b6ddf1` | `960fc2f0e3c98bd9` | `960fc2f0e3c98bd9` | `960fc2f0e3c98bd9` |
| PR AUC | 0.9798 | 0.9698 | 0.9795 | 0.9696 |
| ROC AUC | 0.9839 | 0.9776 | 0.9839 | 0.9764 |
| Recall@3FPM | — | 0.6957 | 0.8261 | 0.7826 |
| verdict | — | FAIL | PASS | FAIL |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f8c733f0d9b6ddf1
```
