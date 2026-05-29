# Confirm PASS — 780698fd141c4f78 on `filetypes/python-bytecode`

Cycle `20260526T225233-confirm-780698fd141c4f78` — 2026-05-26T22:52:33Z

PR_AUC held across 3 seeds (orig 0.9996)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `780698fd141c4f78` | `ea98670b79638d4f` | `ea98670b79638d4f` | `ea98670b79638d4f` |
| PR AUC | 0.9996 | 0.9983 | 0.9978 | 0.9989 |
| ROC AUC | 0.9974 | 0.9932 | 0.9914 | 0.9955 |
| Recall@3FPM | — | 0.8776 | 0.8204 | 0.9143 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=780698fd141c4f78
```
