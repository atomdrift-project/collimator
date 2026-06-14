# Confirm PASS — 9bd3624665e04a47 on `filetypes/zip`

Cycle `20260614T040234-confirm-9bd3624665e04a47` — 2026-06-14T04:02:34Z

PR_AUC held across 3 seeds (orig 0.9997)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `9bd3624665e04a47` | `752565af38dd0934` | `752565af38dd0934` | `752565af38dd0934` |
| PR AUC | 0.9997 | 0.9996 | 0.9996 | 0.9996 |
| ROC AUC | 0.9962 | 0.9961 | 0.9964 | 0.9965 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=9bd3624665e04a47
```
