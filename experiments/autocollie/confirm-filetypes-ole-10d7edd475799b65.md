# Confirm PASS — 10d7edd475799b65 on `filetypes/ole`

Cycle `20260628T023456-confirm-10d7edd475799b65` — 2026-06-28T02:34:56Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `10d7edd475799b65` | `dc8ca8f0bb55ab23` | `dc8ca8f0bb55ab23` | `dc8ca8f0bb55ab23` |
| PR AUC | 0.9999 | 0.9999 | 0.9999 | 1.0000 |
| ROC AUC | 0.9991 | 0.9991 | 0.9991 | 0.9991 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=10d7edd475799b65
```
