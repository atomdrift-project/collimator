# Confirm PASS — 64d55601a4572f1c on `filetypes/pkg-info`

Cycle `20260526T201606-confirm-64d55601a4572f1c` — 2026-05-26T20:16:06Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `64d55601a4572f1c` | `838ee6a94ae43a9e` | `838ee6a94ae43a9e` | `838ee6a94ae43a9e` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 1.0000 | 1.0000 | 1.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=64d55601a4572f1c
```
