# Confirm PASS — aebc222dd6246399 on `filetypes/vbs`

Cycle `20260526T222919-confirm-aebc222dd6246399` — 2026-05-26T22:29:19Z

PR_AUC held across 3 seeds (orig 0.9991)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `aebc222dd6246399` | `4a328a326e164d66` | `4a328a326e164d66` | `4a328a326e164d66` |
| PR AUC | 0.9991 | 0.9971 | 0.9958 | 0.9960 |
| ROC AUC | 0.9985 | 0.9810 | 0.9789 | 0.9784 |
| Recall@3FPM | — | 0.3814 | 0.1818 | 0.2106 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=aebc222dd6246399
```
