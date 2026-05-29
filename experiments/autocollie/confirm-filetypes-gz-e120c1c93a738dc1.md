# Confirm PASS — e120c1c93a738dc1 on `filetypes/gz`

Cycle `20260526T205243-confirm-e120c1c93a738dc1` — 2026-05-26T20:52:43Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e120c1c93a738dc1` | `aac33f62a9731d79` | `aac33f62a9731d79` | `aac33f62a9731d79` |
| PR AUC | 1.0000 | 0.9980 | 0.9982 | 0.9981 |
| ROC AUC | 1.0000 | 0.9972 | 0.9976 | 0.9973 |
| Recall@3FPM | — | 0.9826 | 0.9652 | 0.9826 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e120c1c93a738dc1
```
