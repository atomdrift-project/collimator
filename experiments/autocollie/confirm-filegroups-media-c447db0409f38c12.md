# Confirm PASS — c447db0409f38c12 on `filegroups/media`

Cycle `20260527T010022-confirm-c447db0409f38c12` — 2026-05-27T01:00:22Z

PR_AUC held across 3 seeds (orig 0.9986)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c447db0409f38c12` | `58f451111a256318` | `58f451111a256318` | `58f451111a256318` |
| PR AUC | 0.9986 | 0.9987 | 0.9978 | 0.9994 |
| ROC AUC | 0.9984 | 0.9984 | 0.9974 | 0.9993 |
| Recall@3FPM | — | 0.9333 | 0.9333 | 0.9444 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=c447db0409f38c12
```
