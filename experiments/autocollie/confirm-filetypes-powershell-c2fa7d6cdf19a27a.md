# Confirm PASS — c2fa7d6cdf19a27a on `filetypes/powershell`

Cycle `20260527T010547-confirm-c2fa7d6cdf19a27a` — 2026-05-27T01:05:47Z

PR_AUC held across 3 seeds (orig 0.9986)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c2fa7d6cdf19a27a` | `79b3115e8973aaad` | `79b3115e8973aaad` | `79b3115e8973aaad` |
| PR AUC | 0.9986 | 0.9984 | 0.9990 | 0.9983 |
| ROC AUC | 0.9964 | 0.9945 | 0.9967 | 0.9945 |
| Recall@3FPM | — | 0.8006 | 0.8063 | 0.7464 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=c2fa7d6cdf19a27a
```
