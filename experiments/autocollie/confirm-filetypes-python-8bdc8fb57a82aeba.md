# Confirm PASS — 8bdc8fb57a82aeba on `filetypes/python`

Cycle `20260616T102300-confirm-8bdc8fb57a82aeba` — 2026-06-16T10:23:00Z

PR_AUC held across 3 seeds (orig 0.9920)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `8bdc8fb57a82aeba` | `4f72c8d508ca40cb` | `4f72c8d508ca40cb` | `4f72c8d508ca40cb` |
| PR AUC | 0.9920 | 0.9930 | 0.9931 | 0.9927 |
| ROC AUC | 0.9942 | 0.9947 | 0.9949 | 0.9947 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=8bdc8fb57a82aeba
```
