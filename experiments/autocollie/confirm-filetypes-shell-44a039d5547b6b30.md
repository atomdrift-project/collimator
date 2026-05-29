# Confirm PASS — 44a039d5547b6b30 on `filetypes/shell`

Cycle `20260527T010506-confirm-44a039d5547b6b30` — 2026-05-27T01:05:06Z

PR_AUC held across 3 seeds (orig 0.9984)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `44a039d5547b6b30` | `a29a2cfde7f19df4` | `a29a2cfde7f19df4` | `a29a2cfde7f19df4` |
| PR AUC | 0.9984 | 0.9965 | 0.9971 | 0.9971 |
| ROC AUC | 0.9996 | 0.9976 | 0.9980 | 0.9980 |
| Recall@3FPM | — | 0.8852 | 0.8530 | 0.8895 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=44a039d5547b6b30
```
