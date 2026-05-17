# Confirm PASS — bcf04762891c00a0 on `filetypes/python`

Cycle `20260515T115941-confirm-bcf04762891c00a0` — 2026-05-15T11:59:41Z

PR_AUC held across 3 seeds (orig 0.9987)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `bcf04762891c00a0` | `6de9ea671fa2cd23` | `6de9ea671fa2cd23` | `6de9ea671fa2cd23` |
| PR AUC | 0.9987 | 0.9986 | 0.9985 | 0.9987 |
| ROC AUC | 0.9988 | 0.9987 | 0.9986 | 0.9988 |
| Recall@3FPM | — | 0.7589 | 0.7398 | 0.8532 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=bcf04762891c00a0
```
