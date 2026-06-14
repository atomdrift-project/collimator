# Confirm PASS — 2bb4b063701f7ea6 on `filetypes/shell`

Cycle `20260613T192622-confirm-2bb4b063701f7ea6` — 2026-06-13T19:26:22Z

PR_AUC held across 3 seeds (orig 0.9968)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `2bb4b063701f7ea6` | `53a133a9b43a4e70` | `53a133a9b43a4e70` | `53a133a9b43a4e70` |
| PR AUC | 0.9968 | 0.9969 | 0.9968 | 0.9972 |
| ROC AUC | 0.9980 | 0.9971 | 0.9970 | 0.9974 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=2bb4b063701f7ea6
```
