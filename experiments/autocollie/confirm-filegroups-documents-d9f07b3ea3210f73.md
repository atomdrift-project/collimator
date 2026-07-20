# Confirm PASS — d9f07b3ea3210f73 on `filegroups/documents`

Cycle `20260715T131322-confirm-d9f07b3ea3210f73` — 2026-07-15T13:13:22Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d9f07b3ea3210f73` | `a60d6af5687f9172` | `a60d6af5687f9172` | `a60d6af5687f9172` |
| PR AUC | 0.9999 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9990 | 0.9991 | 0.9991 | 0.9991 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d9f07b3ea3210f73
```
