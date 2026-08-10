# Confirm PASS — 27e28a22ce0c06d4 on `filetypes/vbs`

Cycle `20260805T120432-confirm-27e28a22ce0c06d4` — 2026-08-05T12:04:32Z

PR_AUC held across 3 seeds (orig 0.9979)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `27e28a22ce0c06d4` | `038189d3b3c7a012` | `038189d3b3c7a012` | `038189d3b3c7a012` |
| PR AUC | 0.9979 | 0.9988 | 0.9988 | 0.9988 |
| ROC AUC | 0.9921 | 0.9958 | 0.9958 | 0.9957 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=27e28a22ce0c06d4
```
