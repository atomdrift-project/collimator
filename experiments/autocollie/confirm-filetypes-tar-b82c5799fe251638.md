# Confirm PASS — b82c5799fe251638 on `filetypes/tar`

Cycle `20260526T213223-confirm-b82c5799fe251638` — 2026-05-26T21:32:23Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b82c5799fe251638` | `5587649d2d4e2904` | `5587649d2d4e2904` | `5587649d2d4e2904` |
| PR AUC | 1.0000 | 0.9997 | 0.9993 | 0.9997 |
| ROC AUC | 1.0000 | 0.9974 | 0.9934 | 0.9971 |
| Recall@3FPM | — | 0.9803 | 0.9868 | 0.9737 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b82c5799fe251638
```
