# Confirm PASS — 85110ad50c9eca3e on `filetypes/go`

Cycle `20260526T080330-confirm-85110ad50c9eca3e` — 2026-05-26T08:03:30Z

PR_AUC held across 3 seeds (orig 0.9637)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `85110ad50c9eca3e` | `2ec94ef8424ad150` | `2ec94ef8424ad150` | `2ec94ef8424ad150` |
| PR AUC | 0.9637 | 0.9593 | 0.9604 | 0.9599 |
| ROC AUC | 0.9876 | 0.9861 | 0.9869 | 0.9862 |
| Recall@3FPM | — | 0.5241 | 0.4759 | 0.5000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=85110ad50c9eca3e
```
