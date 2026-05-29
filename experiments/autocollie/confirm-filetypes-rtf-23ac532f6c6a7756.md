# Confirm PASS — 23ac532f6c6a7756 on `filetypes/rtf`

Cycle `20260525T214300-confirm-23ac532f6c6a7756` — 2026-05-25T21:43:00Z

PR_AUC held across 3 seeds (orig 0.9780)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `23ac532f6c6a7756` | `803d2b0157ec5b48` | `803d2b0157ec5b48` | `803d2b0157ec5b48` |
| PR AUC | 0.9780 | 0.9784 | 0.9784 | 0.9784 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=23ac532f6c6a7756
```
