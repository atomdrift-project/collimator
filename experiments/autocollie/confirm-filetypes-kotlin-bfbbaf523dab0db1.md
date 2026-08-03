# Confirm PASS — bfbbaf523dab0db1 on `filetypes/kotlin`

Cycle `20260721T080244-confirm-bfbbaf523dab0db1` — 2026-07-21T08:02:44Z

PR_AUC held across 3 seeds (orig 0.9998)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `bfbbaf523dab0db1` | `5277b865d513a125` | `5277b865d513a125` | `5277b865d513a125` |
| PR AUC | 0.9998 | 0.9999 | 1.0000 | 1.0000 |
| ROC AUC | 0.9949 | 0.9951 | 0.9989 | 0.9991 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=bfbbaf523dab0db1
```
