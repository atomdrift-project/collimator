# Confirm PASS — ead91cb9bdd4368a on `filegroups/documents`

Cycle `20260526T222041-confirm-ead91cb9bdd4368a` — 2026-05-26T22:20:41Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ead91cb9bdd4368a` | `38c350e24642cc6f` | `38c350e24642cc6f` | `38c350e24642cc6f` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9991 | 0.9997 | 0.9997 | 0.9997 |
| Recall@3FPM | — | 0.9749 | 0.9758 | 0.9775 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=ead91cb9bdd4368a
```
