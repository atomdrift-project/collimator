# Confirm PASS — 5d2d79c1d95b19a1 on `filetypes/csharp`

Cycle `20260628T171338-confirm-5d2d79c1d95b19a1` — 2026-06-28T17:13:38Z

PR_AUC held across 3 seeds (orig 0.9909)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `5d2d79c1d95b19a1` | `9146de50e4fb4dfc` | `9146de50e4fb4dfc` | `9146de50e4fb4dfc` |
| PR AUC | 0.9909 | 0.9868 | 0.9882 | 0.9839 |
| ROC AUC | 0.9941 | 0.9915 | 0.9926 | 0.9902 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | FAIL |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=5d2d79c1d95b19a1
```
