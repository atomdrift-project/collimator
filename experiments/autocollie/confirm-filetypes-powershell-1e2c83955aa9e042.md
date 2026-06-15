# Confirm PASS — 1e2c83955aa9e042 on `filetypes/powershell`

Cycle `20260615T062907-confirm-1e2c83955aa9e042` — 2026-06-15T06:29:07Z

PR_AUC held across 3 seeds (orig 0.9993)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `1e2c83955aa9e042` | `017faa3520dfcef1` | `017faa3520dfcef1` | `017faa3520dfcef1` |
| PR AUC | 0.9993 | 0.9990 | 0.9994 | 0.9993 |
| ROC AUC | 0.9959 | 0.9948 | 0.9968 | 0.9963 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=1e2c83955aa9e042
```
