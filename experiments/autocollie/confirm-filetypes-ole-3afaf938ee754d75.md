# Confirm PASS — 3afaf938ee754d75 on `filetypes/ole`

Cycle `20260825T212056-confirm-3afaf938ee754d75` — 2026-08-25T21:20:56Z

PR_AUC held across 3 seeds (orig 0.9997)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3afaf938ee754d75` | `6e86a01c2569b817` | `6e86a01c2569b817` | `6e86a01c2569b817` |
| PR AUC | 0.9997 | 0.9997 | 0.9997 | 0.9997 |
| ROC AUC | 0.9991 | 0.9991 | 0.9990 | 0.9991 |
| Recall@L50 | — | 0.9093 | 0.9348 | 0.9190 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3afaf938ee754d75
```
