# Confirm PASS — 8ebbdabe9ffa9182 on `filetypes/msi`

Cycle `20260526T215040-confirm-8ebbdabe9ffa9182` — 2026-05-26T21:50:40Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `8ebbdabe9ffa9182` | `e93c3edc95835111` | `e93c3edc95835111` | `e93c3edc95835111` |
| PR AUC | 1.0000 | 0.9999 | 0.9997 | 0.9999 |
| ROC AUC | 1.0000 | 0.9973 | 0.9922 | 0.9973 |
| Recall@3FPM | — | 0.9900 | 0.9800 | 0.9900 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=8ebbdabe9ffa9182
```
