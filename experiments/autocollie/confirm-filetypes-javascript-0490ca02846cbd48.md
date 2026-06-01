# Confirm PASS — 0490ca02846cbd48 on `filetypes/javascript`

Cycle `20260601T203040-confirm-0490ca02846cbd48` — 2026-06-01T20:30:40Z

PR_AUC held across 3 seeds (orig 0.9988)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0490ca02846cbd48` | `30f982b3ea32330b` | `30f982b3ea32330b` | `30f982b3ea32330b` |
| PR AUC | 0.9988 | 0.9992 | 0.9992 | 0.9992 |
| ROC AUC | 0.9984 | 0.9989 | 0.9989 | 0.9989 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0490ca02846cbd48
```
