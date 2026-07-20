# Confirm PASS — 3001dbf55d0017af on `filetypes/java_class`

Cycle `20260715T065458-confirm-3001dbf55d0017af` — 2026-07-15T06:54:58Z

PR_AUC held across 3 seeds (orig 0.9884)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3001dbf55d0017af` | `0351ce56f97ce362` | `0351ce56f97ce362` | `0351ce56f97ce362` |
| PR AUC | 0.9884 | 0.9884 | 0.9882 | 0.9893 |
| ROC AUC | 0.9979 | 0.9981 | 0.9981 | 0.9984 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3001dbf55d0017af
```
