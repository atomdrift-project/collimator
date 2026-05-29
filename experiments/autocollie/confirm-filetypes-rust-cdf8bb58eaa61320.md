# Confirm PASS — cdf8bb58eaa61320 on `filetypes/rust`

Cycle `20260527T053200-confirm-cdf8bb58eaa61320` — 2026-05-27T05:32:00Z

PR_AUC held across 3 seeds (orig 0.8923)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `cdf8bb58eaa61320` | `8a22ad28dcea0930` | `8a22ad28dcea0930` | `8a22ad28dcea0930` |
| PR AUC | 0.8923 | 0.8771 | 0.6280 | 0.9242 |
| ROC AUC | 0.9862 | 0.9860 | 0.9538 | 0.9895 |
| Recall@3FPM | — | 0.3077 | 0.0769 | 0.5385 |
| verdict | — | FAIL | FAIL | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=cdf8bb58eaa61320
```
