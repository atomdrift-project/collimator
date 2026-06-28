# Confirm PASS — b2c5ebae60db29bf on `filegroups/documents`

Cycle `20260628T135209-confirm-b2c5ebae60db29bf` — 2026-06-28T13:52:09Z

PR_AUC held across 3 seeds (orig 0.9295)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b2c5ebae60db29bf` | `266bdd9b127df2fc` | `266bdd9b127df2fc` | `266bdd9b127df2fc` |
| PR AUC | 0.9295 | 0.9790 | 0.9809 | 0.9791 |
| ROC AUC | 0.8943 | 0.9019 | 0.9128 | 0.9038 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b2c5ebae60db29bf
```
