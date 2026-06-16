# Confirm PASS — 622dcaef385f1b6f on `filegroups/scripts`

Cycle `20260616T092210-confirm-622dcaef385f1b6f` — 2026-06-16T09:22:10Z

PR_AUC held across 3 seeds (orig 0.9961)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `622dcaef385f1b6f` | `6e4b6281bf1d47fa` | `6e4b6281bf1d47fa` | `6e4b6281bf1d47fa` |
| PR AUC | 0.9961 | 0.9982 | 0.9982 | 0.9982 |
| ROC AUC | 0.9956 | 0.9979 | 0.9979 | 0.9979 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=622dcaef385f1b6f
```
