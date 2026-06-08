# Confirm PASS — 7d1893b3c4495137 on `filetypes/xml`

Cycle `20260608T112301-confirm-7d1893b3c4495137` — 2026-06-08T11:23:01Z

PR_AUC held across 3 seeds (orig 0.9952)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `7d1893b3c4495137` | `e73f5797c5266a2e` | `e73f5797c5266a2e` | `e73f5797c5266a2e` |
| PR AUC | 0.9952 | 0.9974 | 0.9959 | 0.9971 |
| ROC AUC | 0.9984 | 0.9992 | 0.9987 | 0.9991 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=7d1893b3c4495137
```
