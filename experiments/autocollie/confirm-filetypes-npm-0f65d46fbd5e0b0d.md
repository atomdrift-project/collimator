# Confirm PASS — 0f65d46fbd5e0b0d on `filetypes/npm`

Cycle `20260627T125642-confirm-0f65d46fbd5e0b0d` — 2026-06-27T12:56:42Z

PR_AUC held across 3 seeds (orig 0.9816)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0f65d46fbd5e0b0d` | `d60ff95449e2dc9e` | `d60ff95449e2dc9e` | `d60ff95449e2dc9e` |
| PR AUC | 0.9816 | 0.9830 | 0.9839 | 0.9846 |
| ROC AUC | 0.9814 | 0.9819 | 0.9837 | 0.9832 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0f65d46fbd5e0b0d
```
