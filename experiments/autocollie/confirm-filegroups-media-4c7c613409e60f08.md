# Confirm PASS — 4c7c613409e60f08 on `filegroups/media`

Cycle `20260527T005652-confirm-4c7c613409e60f08` — 2026-05-27T00:56:52Z

PR_AUC held across 3 seeds (orig 0.9986)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `4c7c613409e60f08` | `954eb6e01ff2eaeb` | `954eb6e01ff2eaeb` | `954eb6e01ff2eaeb` |
| PR AUC | 0.9986 | 0.9987 | 0.9978 | 0.9994 |
| ROC AUC | 0.9984 | 0.9984 | 0.9974 | 0.9993 |
| Recall@3FPM | — | 0.9333 | 0.9333 | 0.9556 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=4c7c613409e60f08
```
