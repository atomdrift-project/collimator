# Confirm PASS — 8b8f845c8b127838 on `filetypes/objc`

Cycle `20260527T071816-confirm-8b8f845c8b127838` — 2026-05-27T07:18:16Z

PR_AUC held across 3 seeds (orig 0.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `8b8f845c8b127838` | `6938105803f09dd6` | `6938105803f09dd6` | `6938105803f09dd6` |
| PR AUC | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| ROC AUC | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=8b8f845c8b127838
```
