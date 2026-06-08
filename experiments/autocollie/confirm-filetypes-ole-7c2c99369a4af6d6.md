# Confirm PASS — 7c2c99369a4af6d6 on `filetypes/ole`

Cycle `20260608T161651-confirm-7c2c99369a4af6d6` — 2026-06-08T16:16:51Z

PR_AUC held across 3 seeds (orig 0.9966)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `7c2c99369a4af6d6` | `026d2496b60b5d52` | `026d2496b60b5d52` | `026d2496b60b5d52` |
| PR AUC | 0.9966 | 0.9973 | 0.9965 | 0.9973 |
| ROC AUC | 0.9960 | 0.9966 | 0.9958 | 0.9966 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=7c2c99369a4af6d6
```
