# Confirm PASS — d3d3d646fe5ccdde on `general`

Cycle `20260616T062613-confirm-d3d3d646fe5ccdde` — 2026-06-16T06:26:13Z

PR_AUC held across 3 seeds (orig 0.9979)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d3d3d646fe5ccdde` | `8a9002927faf8c81` | `8a9002927faf8c81` | `8a9002927faf8c81` |
| PR AUC | 0.9979 | 0.9998 | 0.9998 | 0.9998 |
| ROC AUC | 0.9977 | 0.9993 | 0.9993 | 0.9993 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d3d3d646fe5ccdde
```
