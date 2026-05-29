# Confirm PASS — 02219cb6ba45996a on `filetypes/csharp`

Cycle `20260527T003037-confirm-02219cb6ba45996a` — 2026-05-27T00:30:37Z

PR_AUC held across 3 seeds (orig 0.9869)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `02219cb6ba45996a` | `15268192b9c57ca8` | `15268192b9c57ca8` | `15268192b9c57ca8` |
| PR AUC | 0.9869 | 0.9848 | 0.9850 | 0.9855 |
| ROC AUC | 0.9927 | 0.9918 | 0.9916 | 0.9915 |
| Recall@3FPM | — | 0.7746 | 0.8592 | 0.9155 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=02219cb6ba45996a
```
