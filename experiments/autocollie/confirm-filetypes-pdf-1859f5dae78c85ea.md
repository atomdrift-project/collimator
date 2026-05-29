# Confirm PASS — 1859f5dae78c85ea on `filetypes/pdf`

Cycle `20260526T184603-confirm-1859f5dae78c85ea` — 2026-05-26T18:46:03Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `1859f5dae78c85ea` | `243ef4e7f888dff1` | `243ef4e7f888dff1` | `243ef4e7f888dff1` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 0.9997 | 0.9997 | 0.9997 |
| Recall@3FPM | — | 0.9877 | 0.9877 | 0.9881 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=1859f5dae78c85ea
```
