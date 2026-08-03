# Confirm PASS — 96b3d30dae2eaaee on `filetypes/pdf`

Cycle `20260727T025324-confirm-96b3d30dae2eaaee` — 2026-07-27T02:53:24Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `96b3d30dae2eaaee` | `e7f94b68a5acdbb0` | `e7f94b68a5acdbb0` | `e7f94b68a5acdbb0` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9991 | 0.9992 | 0.9992 | 0.9992 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=96b3d30dae2eaaee
```
