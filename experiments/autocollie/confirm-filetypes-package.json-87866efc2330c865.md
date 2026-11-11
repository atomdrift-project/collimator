# Confirm PASS — 87866efc2330c865 on `filetypes/package.json`

Cycle `20261106T195434-confirm-87866efc2330c865` — 2026-11-06T19:54:34Z

averaged 3-seed ensemble PR_AUC held: 0.9986 -> 0.9982; individual seeds may be noisy

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `87866efc2330c865` | `1ed6c3d710941b66` | `1ed6c3d710941b66` | `1ed6c3d710941b66` |
| PR AUC | 0.9986 | 0.9982 | 0.9976 | 0.9973 |
| ROC AUC | 0.9993 | 0.9993 | 0.9988 | 0.9988 |
| Recall@L50 | — | 0.6784 | 0.5799 | 0.6012 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=87866efc2330c865
```
