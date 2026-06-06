# Confirm PASS — 2e0dbc94ef2379a6 on `filetypes/plist`

Cycle `20260606T111120-confirm-2e0dbc94ef2379a6` — 2026-06-06T11:11:20Z

PR_AUC held across 3 seeds (orig 0.2320)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `2e0dbc94ef2379a6` | `8948dc2af66b4f4d` | `8948dc2af66b4f4d` | `8948dc2af66b4f4d` |
| PR AUC | 0.2320 | 0.2124 | 0.2406 | 0.2417 |
| ROC AUC | 0.7161 | 0.7950 | 0.7530 | 0.7723 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=2e0dbc94ef2379a6
```
