# Confirm PASS — 1f9ee448fdf4f9e3 on `filegroups/source`

Cycle `20260525T152234-confirm-1f9ee448fdf4f9e3` — 2026-05-25T15:22:34Z

PR_AUC held across 3 seeds (orig 0.9988)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `1f9ee448fdf4f9e3` | `4238aae72b541df4` | `4238aae72b541df4` | `4238aae72b541df4` |
| PR AUC | 0.9988 | 0.9992 | 0.9991 | 0.9991 |
| ROC AUC | 0.9982 | 0.9984 | 0.9983 | 0.9984 |
| Recall@3FPM | — | 0.9172 | 0.9353 | 0.9256 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=1f9ee448fdf4f9e3
```
