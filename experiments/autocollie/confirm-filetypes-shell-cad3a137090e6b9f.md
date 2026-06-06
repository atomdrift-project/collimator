# Confirm PASS — cad3a137090e6b9f on `filetypes/shell`

Cycle `20260606T150509-confirm-cad3a137090e6b9f` — 2026-06-06T15:05:09Z

PR_AUC held across 3 seeds (orig 0.9960)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `cad3a137090e6b9f` | `774524474e433510` | `774524474e433510` | `774524474e433510` |
| PR AUC | 0.9960 | 0.9986 | 0.9985 | 0.9987 |
| ROC AUC | 0.9974 | 0.9986 | 0.9986 | 0.9987 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=cad3a137090e6b9f
```
