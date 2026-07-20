# Confirm PASS — 7ed85f7da9a6922d on `filegroups/scripts`

Cycle `20260713T070929-confirm-7ed85f7da9a6922d` — 2026-07-13T07:09:29Z

PR_AUC held across 3 seeds (orig 0.9935)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `7ed85f7da9a6922d` | `66497eec6ab1115d` | `66497eec6ab1115d` | `66497eec6ab1115d` |
| PR AUC | 0.9935 | 0.9949 | 0.9948 | 0.9949 |
| ROC AUC | 0.9921 | 0.9960 | 0.9959 | 0.9959 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=7ed85f7da9a6922d
```
