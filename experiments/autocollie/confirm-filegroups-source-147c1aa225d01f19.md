# Confirm PASS — 147c1aa225d01f19 on `filegroups/source`

Cycle `20260614T202031-confirm-147c1aa225d01f19` — 2026-06-14T20:20:31Z

PR_AUC held across 3 seeds (orig 0.9990)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `147c1aa225d01f19` | `6ceb25c7b0aa8b0a` | `6ceb25c7b0aa8b0a` | `6ceb25c7b0aa8b0a` |
| PR AUC | 0.9990 | 0.9975 | 0.9975 | 0.9974 |
| ROC AUC | 0.9983 | 0.9972 | 0.9971 | 0.9971 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=147c1aa225d01f19
```
