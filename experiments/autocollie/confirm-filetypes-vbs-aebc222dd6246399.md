# Confirm PASS — aebc222dd6246399 on `filetypes/vbs`

Cycle `20260602T010450-confirm-aebc222dd6246399` — 2026-06-02T01:04:50Z

PR_AUC held across 3 seeds (orig 0.9991)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `aebc222dd6246399` | `85476f6f8abb2d63` | `85476f6f8abb2d63` | `85476f6f8abb2d63` |
| PR AUC | 0.9991 | 0.9976 | 0.9975 | 0.9979 |
| ROC AUC | 0.9985 | 0.9641 | 0.9615 | 0.9692 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=aebc222dd6246399
```
