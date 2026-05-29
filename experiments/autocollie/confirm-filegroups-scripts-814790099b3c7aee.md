# Confirm PASS — 814790099b3c7aee on `filegroups/scripts`

Cycle `20260526T055257-confirm-814790099b3c7aee` — 2026-05-26T05:52:57Z

PR_AUC held across 3 seeds (orig 0.9979)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `814790099b3c7aee` | `c6c8cb7e7803392d` | `c6c8cb7e7803392d` | `c6c8cb7e7803392d` |
| PR AUC | 0.9979 | 0.9992 | 0.9992 | 0.9992 |
| ROC AUC | 0.9977 | 0.9991 | 0.9991 | 0.9991 |
| Recall@3FPM | — | 0.6699 | 0.7745 | 0.7263 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=814790099b3c7aee
```
