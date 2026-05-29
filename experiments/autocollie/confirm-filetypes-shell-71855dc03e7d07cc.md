# Confirm PASS — 71855dc03e7d07cc on `filetypes/shell`

Cycle `20260527T010442-confirm-71855dc03e7d07cc` — 2026-05-27T01:04:42Z

PR_AUC held across 3 seeds (orig 0.9986)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `71855dc03e7d07cc` | `d11ea99b934ebb12` | `d11ea99b934ebb12` | `d11ea99b934ebb12` |
| PR AUC | 0.9986 | 0.9969 | 0.9970 | 0.9970 |
| ROC AUC | 0.9996 | 0.9979 | 0.9979 | 0.9979 |
| Recall@3FPM | — | 0.8734 | 0.8305 | 0.8455 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=71855dc03e7d07cc
```
