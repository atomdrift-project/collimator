# Confirm PASS — 173f995145e67b0b on `filetypes/vbs`

Cycle `20260608T110824-confirm-173f995145e67b0b` — 2026-06-08T11:08:24Z

PR_AUC held across 3 seeds (orig 0.9976)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `173f995145e67b0b` | `a49a77dc8c78b6d6` | `a49a77dc8c78b6d6` | `a49a77dc8c78b6d6` |
| PR AUC | 0.9976 | 0.9976 | 0.9972 | 0.9973 |
| ROC AUC | 0.9919 | 0.9919 | 0.9903 | 0.9909 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=173f995145e67b0b
```
