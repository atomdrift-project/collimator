# Confirm PASS — eb8527fe18100b23 on `filetypes/objc`

Cycle `20260508T090041-confirm-eb8527fe18100b23` — 2026-05-08T09:00:41Z

F1 held across 3 seeds (orig 0.6667)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `eb8527fe18100b23` | `bc3f462eb34e9e15` | `af5f17140800d653` | `2a72e069794e3ceb` |
| F1 | 0.6667 | 0.6667 | 0.6667 | 0.6667 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| AP | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| recall@3 FP/M | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=eb8527fe18100b23
```
