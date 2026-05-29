# Confirm PASS — 9e97ad28981f3c90 on `filetypes/tar`

Cycle `20260526T214237-confirm-9e97ad28981f3c90` — 2026-05-26T21:42:37Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `9e97ad28981f3c90` | `d26bfd023174a69b` | `d26bfd023174a69b` | `d26bfd023174a69b` |
| PR AUC | 1.0000 | 0.9999 | 0.9997 | 0.9999 |
| ROC AUC | 1.0000 | 0.9993 | 0.9971 | 0.9993 |
| Recall@3FPM | — | 0.9868 | 0.9868 | 0.9868 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=9e97ad28981f3c90
```
