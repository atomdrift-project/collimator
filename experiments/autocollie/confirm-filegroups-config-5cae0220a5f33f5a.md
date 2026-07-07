# Confirm PASS — 5cae0220a5f33f5a on `filegroups/config`

Cycle `20260706T053347-confirm-5cae0220a5f33f5a` — 2026-07-06T05:33:47Z

PR_AUC held across 3 seeds (orig 0.9972)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `5cae0220a5f33f5a` | `d9b7eaeb7b3c761f` | `d9b7eaeb7b3c761f` | `d9b7eaeb7b3c761f` |
| PR AUC | 0.9972 | 0.9973 | 0.9973 | 0.9974 |
| ROC AUC | 0.9976 | 0.9978 | 0.9975 | 0.9978 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=5cae0220a5f33f5a
```
