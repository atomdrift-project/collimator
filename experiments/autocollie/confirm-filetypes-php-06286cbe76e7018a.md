# Confirm PASS — 06286cbe76e7018a on `filetypes/php`

Cycle `20260706T083543-confirm-06286cbe76e7018a` — 2026-07-06T08:35:43Z

PR_AUC held across 3 seeds (orig 0.9836)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `06286cbe76e7018a` | `125e51db04aebdae` | `125e51db04aebdae` | `125e51db04aebdae` |
| PR AUC | 0.9836 | 0.9860 | 0.9852 | 0.9856 |
| ROC AUC | 0.9959 | 0.9964 | 0.9959 | 0.9964 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=06286cbe76e7018a
```
