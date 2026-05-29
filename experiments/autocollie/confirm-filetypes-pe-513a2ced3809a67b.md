# Confirm PASS — 513a2ced3809a67b on `filetypes/pe`

Cycle `20260526T110641-confirm-513a2ced3809a67b` — 2026-05-26T11:06:41Z

PR_AUC held across 3 seeds (orig 0.9997)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `513a2ced3809a67b` | `05dadb7b6a8e496c` | `05dadb7b6a8e496c` | `05dadb7b6a8e496c` |
| PR AUC | 0.9997 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9997 | 0.9999 | 0.9999 | 0.9999 |
| Recall@3FPM | — | 0.8581 | 0.8420 | 0.8786 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=513a2ced3809a67b
```
