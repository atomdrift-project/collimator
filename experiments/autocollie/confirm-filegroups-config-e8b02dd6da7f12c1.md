# Confirm PASS — e8b02dd6da7f12c1 on `filegroups/config`

Cycle `20260515T055426-confirm-e8b02dd6da7f12c1` — 2026-05-15T05:54:26Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e8b02dd6da7f12c1` | `ffbbb934ef2b7bad` | `ffbbb934ef2b7bad` | `ffbbb934ef2b7bad` |
| PR AUC | 0.9999 | 0.9998 | 0.9999 | 0.9999 |
| ROC AUC | 0.9997 | 0.9997 | 0.9997 | 0.9997 |
| Recall@3FPM | — | 0.9265 | 0.9478 | 0.9659 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e8b02dd6da7f12c1
```
