# Confirm PASS — 001b2348cdbd091f on `filetypes/tar.gz`

Cycle `20260527T021201-confirm-001b2348cdbd091f` — 2026-05-27T02:12:01Z

PR_AUC held across 3 seeds (orig 0.9994)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `001b2348cdbd091f` | `f9f37925dea37e98` | `f9f37925dea37e98` | `f9f37925dea37e98` |
| PR AUC | 0.9994 | 0.9994 | 0.9994 | 0.9994 |
| ROC AUC | 0.9988 | 0.9988 | 0.9988 | 0.9988 |
| Recall@3FPM | — | 0.7003 | 0.7225 | 0.6912 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=001b2348cdbd091f
```
