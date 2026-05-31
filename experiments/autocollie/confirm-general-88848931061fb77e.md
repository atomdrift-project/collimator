# Confirm PASS — 88848931061fb77e on `general`

Cycle `20260530T181834-confirm-88848931061fb77e` — 2026-05-30T18:18:34Z

PR_AUC held across 3 seeds (orig 0.9996)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `88848931061fb77e` | `d4953d6a44dd18c0` | `d4953d6a44dd18c0` | `d4953d6a44dd18c0` |
| PR AUC | 0.9996 | 0.9997 | 0.9997 | 0.9997 |
| ROC AUC | 0.9997 | 0.9992 | 0.9992 | 0.9991 |
| Recall@3FPM | — | 0.3791 | 0.5119 | 0.4986 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=88848931061fb77e
```
