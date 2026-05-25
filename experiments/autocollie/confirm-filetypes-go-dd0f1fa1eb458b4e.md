# Confirm PASS — dd0f1fa1eb458b4e on `filetypes/go`

Cycle `20260525T002556-confirm-dd0f1fa1eb458b4e` — 2026-05-25T00:25:56Z

PR_AUC held across 3 seeds (orig 0.9590)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `dd0f1fa1eb458b4e` | `32b40c1ffcf50f2e` | `32b40c1ffcf50f2e` | `32b40c1ffcf50f2e` |
| PR AUC | 0.9590 | 0.9593 | 0.9575 | 0.9586 |
| ROC AUC | 0.9859 | 0.9860 | 0.9860 | 0.9860 |
| Recall@3FPM | — | 0.5181 | 0.4880 | 0.4699 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=dd0f1fa1eb458b4e
```
