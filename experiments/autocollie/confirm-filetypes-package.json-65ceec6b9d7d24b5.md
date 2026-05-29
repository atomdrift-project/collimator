# Confirm PASS — 65ceec6b9d7d24b5 on `filetypes/package.json`

Cycle `20260525T193340-confirm-65ceec6b9d7d24b5` — 2026-05-25T19:33:40Z

PR_AUC held across 3 seeds (orig 0.9998)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `65ceec6b9d7d24b5` | `1fa83793f517d4a6` | `1fa83793f517d4a6` | `1fa83793f517d4a6` |
| PR AUC | 0.9998 | 0.9999 | 0.9999 | 0.9997 |
| ROC AUC | 0.9997 | 0.9998 | 0.9997 | 0.9992 |
| Recall@3FPM | — | 0.9665 | 0.9682 | 0.9673 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=65ceec6b9d7d24b5
```
