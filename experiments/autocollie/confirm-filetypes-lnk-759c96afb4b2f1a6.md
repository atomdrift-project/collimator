# Confirm PASS — 759c96afb4b2f1a6 on `filetypes/lnk`

Cycle `20260526T235845-confirm-759c96afb4b2f1a6` — 2026-05-26T23:58:45Z

PR_AUC held across 3 seeds (orig 0.9989)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `759c96afb4b2f1a6` | `42997a7045257c77` | `42997a7045257c77` | `42997a7045257c77` |
| PR AUC | 0.9989 | 0.9987 | 0.9990 | 0.9989 |
| ROC AUC | 0.9860 | 0.9826 | 0.9870 | 0.9860 |
| Recall@3FPM | — | 0.9128 | 0.9590 | 0.9487 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=759c96afb4b2f1a6
```
