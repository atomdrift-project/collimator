# Confirm PASS — 53bd56856c78331d on `filetypes/zip`

Cycle `20260606T160027-confirm-53bd56856c78331d` — 2026-06-06T16:00:27Z

PR_AUC held across 3 seeds (orig 0.9997)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `53bd56856c78331d` | `95f25403ec7b41cb` | `95f25403ec7b41cb` | `95f25403ec7b41cb` |
| PR AUC | 0.9997 | 0.9996 | 0.9996 | 0.9996 |
| ROC AUC | 0.9961 | 0.9956 | 0.9960 | 0.9961 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=53bd56856c78331d
```
