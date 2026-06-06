# Confirm PASS — 76c3284340d29531 on `filegroups/config`

Cycle `20260606T074125-confirm-76c3284340d29531` — 2026-06-06T07:41:25Z

PR_AUC held across 3 seeds (orig 0.9989)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `76c3284340d29531` | `af003d64cc815511` | `af003d64cc815511` | `af003d64cc815511` |
| PR AUC | 0.9989 | 0.9990 | 0.9988 | 0.9989 |
| ROC AUC | 0.9983 | 0.9985 | 0.9982 | 0.9983 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=76c3284340d29531
```
