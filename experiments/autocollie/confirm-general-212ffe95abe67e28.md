# Confirm PASS — 212ffe95abe67e28 on `general`

Cycle `20260524T204517-confirm-212ffe95abe67e28` — 2026-05-24T20:45:17Z

PR_AUC held across 3 seeds (orig 0.9988)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `212ffe95abe67e28` | `2320e751fe2323be` | `2320e751fe2323be` | `2320e751fe2323be` |
| PR AUC | 0.9988 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9988 | 0.9997 | 0.9997 | 0.9997 |
| Recall@3FPM | — | 0.6042 | 0.6032 | 0.5779 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=212ffe95abe67e28
```
