# Confirm PASS — 44397b9af19069a5 on `filetypes/ole`

Cycle `20260608T073301-confirm-44397b9af19069a5` — 2026-06-08T07:33:01Z

PR_AUC held across 3 seeds (orig 0.9968)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `44397b9af19069a5` | `c75c224286d6e70a` | `c75c224286d6e70a` | `c75c224286d6e70a` |
| PR AUC | 0.9968 | 0.9971 | 0.9965 | 0.9971 |
| ROC AUC | 0.9961 | 0.9965 | 0.9957 | 0.9965 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=44397b9af19069a5
```
