# Confirm PASS — 3756df39c21e31a8 on `filetypes/go`

Cycle `20260602T005818-confirm-3756df39c21e31a8` — 2026-06-02T00:58:18Z

PR_AUC held across 3 seeds (orig 0.9613)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3756df39c21e31a8` | `ae3076975fd524b4` | `ae3076975fd524b4` | `ae3076975fd524b4` |
| PR AUC | 0.9613 | 0.9634 | 0.9599 | 0.9575 |
| ROC AUC | 0.9867 | 0.9897 | 0.9882 | 0.9881 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3756df39c21e31a8
```
