# Confirm PASS — 13f2088aa1f9ec1f on `filetypes/python-bytecode`

Cycle `20260720T114957-confirm-13f2088aa1f9ec1f` — 2026-07-20T11:49:57Z

PR_AUC held across 3 seeds (orig 0.9961)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `13f2088aa1f9ec1f` | `4b5cc51b957c4d46` | `4b5cc51b957c4d46` | `4b5cc51b957c4d46` |
| PR AUC | 0.9961 | 0.9954 | 0.9921 | 0.9941 |
| ROC AUC | 0.9987 | 0.9985 | 0.9957 | 0.9979 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=13f2088aa1f9ec1f
```
