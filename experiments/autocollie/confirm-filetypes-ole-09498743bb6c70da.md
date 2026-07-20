# Confirm PASS — 09498743bb6c70da on `filetypes/ole`

Cycle `20260711T134518-confirm-09498743bb6c70da` — 2026-07-11T13:45:18Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `09498743bb6c70da` | `766419fcf7d612d7` | `766419fcf7d612d7` | `766419fcf7d612d7` |
| PR AUC | 0.9999 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9991 | 0.9990 | 0.9990 | 0.9990 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=09498743bb6c70da
```
