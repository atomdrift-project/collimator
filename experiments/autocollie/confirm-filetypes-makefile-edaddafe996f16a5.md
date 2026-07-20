# Confirm PASS — edaddafe996f16a5 on `filetypes/makefile`

Cycle `20260720T112900-confirm-edaddafe996f16a5` — 2026-07-20T11:29:00Z

PR_AUC held across 3 seeds (orig 0.4306)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `edaddafe996f16a5` | `af3e2f07e7483e2a` | `af3e2f07e7483e2a` | `af3e2f07e7483e2a` |
| PR AUC | 0.4306 | 0.6699 | 0.5496 | 0.4034 |
| ROC AUC | 0.8594 | 0.9237 | 0.9257 | 0.6867 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | FAIL |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=edaddafe996f16a5
```
