# Confirm PASS — d9b41814c0ffac12 on `filegroups/source`

Cycle `20260704T081003-confirm-d9b41814c0ffac12` — 2026-07-04T08:10:03Z

PR_AUC held across 3 seeds (orig 0.9991)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d9b41814c0ffac12` | `1eba2caf8d8eaca6` | `1eba2caf8d8eaca6` | `1eba2caf8d8eaca6` |
| PR AUC | 0.9991 | 0.9960 | 0.9960 | 0.9960 |
| ROC AUC | 0.9983 | 0.9964 | 0.9964 | 0.9964 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d9b41814c0ffac12
```
