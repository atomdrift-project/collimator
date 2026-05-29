# Confirm PASS — cf2a620dd34ab639 on `filetypes/elf`

Cycle `20260526T160757-confirm-cf2a620dd34ab639` — 2026-05-26T16:07:57Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `cf2a620dd34ab639` | `0492b2214b18eabc` | `0492b2214b18eabc` | `0492b2214b18eabc` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 0.9754 | 0.9802 | 0.9838 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=cf2a620dd34ab639
```
