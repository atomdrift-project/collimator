# Confirm PASS — 3aa7d589cb9f41f4 on `filetypes/plist`

Cycle `20260606T022912-confirm-3aa7d589cb9f41f4` — 2026-06-06T02:29:12Z

PR_AUC held across 3 seeds (orig 0.2284)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3aa7d589cb9f41f4` | `a282e521a7f825b6` | `a282e521a7f825b6` | `a282e521a7f825b6` |
| PR AUC | 0.2284 | 0.2238 | 0.2291 | 0.2381 |
| ROC AUC | 0.6945 | 0.8023 | 0.7310 | 0.7852 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3aa7d589cb9f41f4
```
