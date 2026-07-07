# Confirm PASS — 05d1d634e1160aab on `filetypes/xls`

Cycle `20260705T170046-confirm-05d1d634e1160aab` — 2026-07-05T17:00:46Z

PR_AUC held across 3 seeds (orig 0.9969)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `05d1d634e1160aab` | `2150cec0e3f74b61` | `2150cec0e3f74b61` | `2150cec0e3f74b61` |
| PR AUC | 0.9969 | 0.9973 | 0.9974 | 0.9973 |
| ROC AUC | 0.9910 | 0.9914 | 0.9915 | 0.9912 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=05d1d634e1160aab
```
