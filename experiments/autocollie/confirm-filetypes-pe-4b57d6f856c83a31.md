# Confirm PASS — 4b57d6f856c83a31 on `filetypes/pe`

Cycle `20260824T220211-confirm-4b57d6f856c83a31` — 2026-08-24T22:02:11Z

PR_AUC held across 3 seeds (orig 0.9990)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `4b57d6f856c83a31` | `1a5875eafa5c5892` | `1a5875eafa5c5892` | `1a5875eafa5c5892` |
| PR AUC | 0.9990 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9990 | 0.9997 | 0.9997 | 0.9997 |
| Recall@L50 | — | 0.7376 | 0.6580 | 0.6955 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=4b57d6f856c83a31
```
