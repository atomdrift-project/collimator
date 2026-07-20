# Confirm PASS — b79749c39df8b5a3 on `filetypes/batch`

Cycle `20260715T181738-confirm-b79749c39df8b5a3` — 2026-07-15T18:17:38Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b79749c39df8b5a3` | `4c36208c7d6bd3bd` | `4c36208c7d6bd3bd` | `4c36208c7d6bd3bd` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9989 | 0.9989 | 0.9991 | 0.9990 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b79749c39df8b5a3
```
