# Confirm PASS — c21b2869af6822c1 on `filetypes/go`

Cycle `20260525T160856-confirm-c21b2869af6822c1` — 2026-05-25T16:08:56Z

PR_AUC held across 3 seeds (orig 0.9652)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c21b2869af6822c1` | `7d097d5da3870277` | `7d097d5da3870277` | `7d097d5da3870277` |
| PR AUC | 0.9652 | 0.9629 | 0.9608 | 0.9642 |
| ROC AUC | 0.9882 | 0.9876 | 0.9873 | 0.9879 |
| Recall@3FPM | — | 0.5120 | 0.5000 | 0.5542 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=c21b2869af6822c1
```
