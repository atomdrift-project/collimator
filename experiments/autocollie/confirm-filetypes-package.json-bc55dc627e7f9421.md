# Confirm PASS — bc55dc627e7f9421 on `filetypes/package.json`

Cycle `20260522T164710-confirm-bc55dc627e7f9421` — 2026-05-22T16:47:10Z

PR_AUC held across 3 seeds (orig 0.9997)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `bc55dc627e7f9421` | `5bd13df6024a9637` | `5bd13df6024a9637` | `5bd13df6024a9637` |
| PR AUC | 0.9997 | 0.9997 | 0.9997 | 0.9996 |
| ROC AUC | 0.9994 | 0.9994 | 0.9993 | 0.9992 |
| Recall@3FPM | — | 0.9726 | 0.9704 | 0.9797 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=bc55dc627e7f9421
```
