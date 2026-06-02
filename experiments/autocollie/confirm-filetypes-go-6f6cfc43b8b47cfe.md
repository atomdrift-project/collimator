# Confirm PASS — 6f6cfc43b8b47cfe on `filetypes/go`

Cycle `20260602T010302-confirm-6f6cfc43b8b47cfe` — 2026-06-02T01:03:02Z

PR_AUC held across 3 seeds (orig 0.9575)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6f6cfc43b8b47cfe` | `4f07442dc1938c2d` | `4f07442dc1938c2d` | `4f07442dc1938c2d` |
| PR AUC | 0.9575 | 0.9594 | 0.9549 | 0.9533 |
| ROC AUC | 0.9847 | 0.9883 | 0.9869 | 0.9866 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=6f6cfc43b8b47cfe
```
