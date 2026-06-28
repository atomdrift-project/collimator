# Confirm PASS — 89ff83fb2785f5ad on `filetypes/javascript`

Cycle `20260628T122308-confirm-89ff83fb2785f5ad` — 2026-06-28T12:23:08Z

PR_AUC held across 3 seeds (orig 0.9978)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `89ff83fb2785f5ad` | `ca64ce6dbfc85299` | `ca64ce6dbfc85299` | `ca64ce6dbfc85299` |
| PR AUC | 0.9978 | 0.9990 | 0.9990 | 0.9990 |
| ROC AUC | 0.9974 | 0.9989 | 0.9988 | 0.9988 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=89ff83fb2785f5ad
```
