# Confirm PASS — 4fae5769dde62e05 on `filetypes/jar`

Cycle `20260527T000220-confirm-4fae5769dde62e05` — 2026-05-27T00:02:20Z

PR_AUC held across 3 seeds (orig 0.9985)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `4fae5769dde62e05` | `91f0c6b6db1d5439` | `91f0c6b6db1d5439` | `91f0c6b6db1d5439` |
| PR AUC | 0.9985 | 0.9974 | 0.9980 | 0.9980 |
| ROC AUC | 0.9972 | 0.9946 | 0.9963 | 0.9963 |
| Recall@3FPM | — | 0.8693 | 0.8409 | 0.8807 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=4fae5769dde62e05
```
