# Confirm PASS — adc95a531472c635 on `filetypes/javascript`

Cycle `20260704T084210-confirm-adc95a531472c635` — 2026-07-04T08:42:10Z

PR_AUC held across 3 seeds (orig 0.9993)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `adc95a531472c635` | `0307a37a5ab79c64` | `0307a37a5ab79c64` | `0307a37a5ab79c64` |
| PR AUC | 0.9993 | 0.9988 | 0.9988 | 0.9987 |
| ROC AUC | 0.9989 | 0.9986 | 0.9986 | 0.9985 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=adc95a531472c635
```
