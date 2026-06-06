# Confirm PASS — 7948ea6c6093ee73 on `filetypes/shell`

Cycle `20260606T111432-confirm-7948ea6c6093ee73` — 2026-06-06T11:14:32Z

PR_AUC held across 3 seeds (orig 0.9989)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `7948ea6c6093ee73` | `f128cff11d3f6763` | `f128cff11d3f6763` | `f128cff11d3f6763` |
| PR AUC | 0.9989 | 0.9989 | 0.9989 | 0.9989 |
| ROC AUC | 0.9989 | 0.9990 | 0.9990 | 0.9990 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=7948ea6c6093ee73
```
