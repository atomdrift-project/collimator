# Confirm PASS — 50097d8d87420c6d on `general`

Cycle `20260527T023120-confirm-50097d8d87420c6d` — 2026-05-27T02:31:20Z

PR_AUC held across 3 seeds (orig 0.9988)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `50097d8d87420c6d` | `a03f64b1f2a8a5a3` | `a03f64b1f2a8a5a3` | `a03f64b1f2a8a5a3` |
| PR AUC | 0.9988 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9988 | 0.9995 | 0.9996 | 0.9996 |
| Recall@3FPM | — | 0.6519 | 0.7060 | 0.7488 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=50097d8d87420c6d
```
