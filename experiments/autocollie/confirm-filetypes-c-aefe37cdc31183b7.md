# Confirm PASS — aefe37cdc31183b7 on `filetypes/c`

Cycle `20260526T041118-confirm-aefe37cdc31183b7` — 2026-05-26T04:11:18Z

PR_AUC held across 3 seeds (orig 0.9909)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `aefe37cdc31183b7` | `bc94610068f882e8` | `bc94610068f882e8` | `bc94610068f882e8` |
| PR AUC | 0.9909 | 0.9920 | 0.9913 | 0.9918 |
| ROC AUC | 0.9951 | 0.9958 | 0.9953 | 0.9956 |
| Recall@3FPM | — | 0.7917 | 0.7801 | 0.7963 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=aefe37cdc31183b7
```
