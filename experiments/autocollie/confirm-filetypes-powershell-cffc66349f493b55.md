# Confirm PASS — cffc66349f493b55 on `filetypes/powershell`

Cycle `20260723T035844-confirm-cffc66349f493b55` — 2026-07-23T03:58:44Z

PR_AUC held across 3 seeds (orig 0.9986)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `cffc66349f493b55` | `9d6f1d90a035bce1` | `9d6f1d90a035bce1` | `9d6f1d90a035bce1` |
| PR AUC | 0.9986 | 0.9987 | 0.9990 | 0.9986 |
| ROC AUC | 0.9948 | 0.9950 | 0.9959 | 0.9948 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=cffc66349f493b55
```
