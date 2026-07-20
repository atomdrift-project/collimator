# Confirm PASS — 43a20056004e6c5b on `filegroups/config`

Cycle `20260711T082849-confirm-43a20056004e6c5b` — 2026-07-11T08:28:49Z

PR_AUC held across 3 seeds (orig 0.9974)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `43a20056004e6c5b` | `8d988bdda8f0ea25` | `8d988bdda8f0ea25` | `8d988bdda8f0ea25` |
| PR AUC | 0.9974 | 0.9971 | 0.9970 | 0.9972 |
| ROC AUC | 0.9980 | 0.9976 | 0.9975 | 0.9976 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=43a20056004e6c5b
```
