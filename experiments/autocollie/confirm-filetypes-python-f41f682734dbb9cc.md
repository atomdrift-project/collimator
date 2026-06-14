# Confirm PASS — f41f682734dbb9cc on `filetypes/python`

Cycle `20260613T233801-confirm-f41f682734dbb9cc` — 2026-06-13T23:38:01Z

PR_AUC held across 3 seeds (orig 0.9942)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f41f682734dbb9cc` | `f29bf37d6ca1e980` | `f29bf37d6ca1e980` | `f29bf37d6ca1e980` |
| PR AUC | 0.9942 | 0.9905 | 0.9907 | 0.9908 |
| ROC AUC | 0.9953 | 0.9931 | 0.9933 | 0.9933 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f41f682734dbb9cc
```
