# Confirm PASS — 53b8829766aad307 on `filetypes/xls`

Cycle `20260606T111736-confirm-53b8829766aad307` — 2026-06-06T11:17:36Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `53b8829766aad307` | `9e4f095bd4312db5` | `9e4f095bd4312db5` | `9e4f095bd4312db5` |
| PR AUC | 0.9999 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9992 | 0.9993 | 0.9993 | 0.9994 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=53b8829766aad307
```
