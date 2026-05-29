# Confirm PASS — 94a13ca6b2ea2c89 on `filetypes/python`

Cycle `20260527T002257-confirm-94a13ca6b2ea2c89` — 2026-05-27T00:22:57Z

PR_AUC held across 3 seeds (orig 0.9990)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `94a13ca6b2ea2c89` | `3a46fd52b4464b1f` | `3a46fd52b4464b1f` | `3a46fd52b4464b1f` |
| PR AUC | 0.9990 | 0.9984 | 0.9983 | 0.9984 |
| ROC AUC | 0.9991 | 0.9986 | 0.9985 | 0.9985 |
| Recall@3FPM | — | 0.8073 | 0.7912 | 0.7496 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=94a13ca6b2ea2c89
```
