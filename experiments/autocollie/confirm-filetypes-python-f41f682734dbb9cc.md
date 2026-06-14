# Confirm PASS — f41f682734dbb9cc on `filetypes/python`

Cycle `20260614T043803-confirm-f41f682734dbb9cc` — 2026-06-14T04:38:03Z

PR_AUC held across 3 seeds (orig 0.9942)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f41f682734dbb9cc` | `2c85d43d51b812f5` | `2c85d43d51b812f5` | `2c85d43d51b812f5` |
| PR AUC | 0.9942 | 0.9922 | 0.9922 | 0.9924 |
| ROC AUC | 0.9953 | 0.9943 | 0.9942 | 0.9944 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f41f682734dbb9cc
```
