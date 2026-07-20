# Confirm PASS — 72c2f12b61317657 on `filetypes/json`

Cycle `20260718T140653-confirm-72c2f12b61317657` — 2026-07-18T14:06:53Z

PR_AUC held across 3 seeds (orig 0.9560)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `72c2f12b61317657` | `cb093a9be1812e22` | `cb093a9be1812e22` | `cb093a9be1812e22` |
| PR AUC | 0.9560 | 0.9672 | 0.9680 | 0.9669 |
| ROC AUC | 0.9714 | 0.9706 | 0.9746 | 0.9746 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=72c2f12b61317657
```
