# Confirm PASS — a26547c0ac366864 on `filetypes/batch`

Cycle `20260616T090757-confirm-a26547c0ac366864` — 2026-06-16T09:07:57Z

PR_AUC held across 3 seeds (orig 0.9997)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a26547c0ac366864` | `4016ee6e2ee4d5ed` | `4016ee6e2ee4d5ed` | `4016ee6e2ee4d5ed` |
| PR AUC | 0.9997 | 0.9997 | 0.9998 | 0.9997 |
| ROC AUC | 0.9979 | 0.9976 | 0.9984 | 0.9982 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a26547c0ac366864
```
