# Confirm PASS — 12bb5ad690929e4f on `filetypes/zip`

Cycle `20260526T234721-confirm-12bb5ad690929e4f` — 2026-05-26T23:47:21Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `12bb5ad690929e4f` | `6479be22ad76e90d` | `6479be22ad76e90d` | `6479be22ad76e90d` |
| PR AUC | 0.9999 | 0.9997 | 0.9998 | 0.9997 |
| ROC AUC | 0.9976 | 0.9955 | 0.9959 | 0.9955 |
| Recall@3FPM | — | 0.6492 | 0.7016 | 0.6868 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=12bb5ad690929e4f
```
