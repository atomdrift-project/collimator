# Confirm PASS — adc95a531472c635 on `filetypes/javascript`

Cycle `20260601T210138-confirm-adc95a531472c635` — 2026-06-01T21:01:38Z

PR_AUC held across 3 seeds (orig 0.9993)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `adc95a531472c635` | `86f3ee32d6f9c707` | `86f3ee32d6f9c707` | `86f3ee32d6f9c707` |
| PR AUC | 0.9993 | 0.9992 | 0.9992 | 0.9992 |
| ROC AUC | 0.9989 | 0.9989 | 0.9990 | 0.9989 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=adc95a531472c635
```
