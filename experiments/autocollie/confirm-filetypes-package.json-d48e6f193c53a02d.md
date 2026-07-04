# Confirm PASS — d48e6f193c53a02d on `filetypes/package.json`

Cycle `20260704T135204-confirm-d48e6f193c53a02d` — 2026-07-04T13:52:04Z

PR_AUC held across 3 seeds (orig 0.9966)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d48e6f193c53a02d` | `76c5e23773dc1db1` | `76c5e23773dc1db1` | `76c5e23773dc1db1` |
| PR AUC | 0.9966 | 0.9957 | 0.9957 | 0.9955 |
| ROC AUC | 0.9970 | 0.9953 | 0.9954 | 0.9953 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d48e6f193c53a02d
```
